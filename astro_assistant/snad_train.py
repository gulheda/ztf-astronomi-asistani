"""One preregistered field-held-out SNAD nominal/artifact pilot."""
import argparse
import json
from pathlib import Path


def image_features(images):
    import numpy as np
    x=images[...,0]
    flat=x.reshape(len(x),-1)
    center=x[:,28:35,28:35]
    return np.column_stack([np.percentile(flat,p,axis=1) for p in (1,5,25,75,95,99)]+[
        flat.mean(1),flat.std(1),np.abs(flat).mean(1),center.mean((1,2)),center.std((1,2)),
        x.mean(1).std(1),x.mean(2).std(1),np.abs(np.diff(x,axis=1)).mean((1,2)),
        np.abs(np.diff(x,axis=2)).mean((1,2))])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache",type=Path,default=Path("data/raw/snad"))
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--epochs",type=int,default=12)
    args=parser.parse_args()
    if not 1<=args.epochs<=30:
        parser.error("epochs must be 1..30")
    args.output.mkdir(parents=True,exist_ok=False)
    import os
    import numpy as np
    import tensorflow as tf
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (accuracy_score,balanced_accuracy_score,precision_score,recall_score,
        f1_score,roc_auc_score,average_precision_score,confusion_matrix)
    from .snad_dataset import prepare
    tf.keras.utils.set_random_seed(42)
    tf.config.threading.set_intra_op_parallelism_threads(2)
    tf.config.threading.set_inter_op_parallelism_threads(2)
    tf.config.experimental.enable_op_determinism()
    path=prepare(args.cache,args.output/"dataset",seed=42)
    with np.load(path,allow_pickle=False) as data:
        # Monotonic per-pixel compression retains sign and limits dynamic range.
        x=np.arcsinh(data["images"]).astype("float32")
        y=data["labels"]
        split=data["split"]
        objects=data["object_ids"]
        fields=data["field_ids"]
        groups=data["group_ids"]
    ids={name:np.flatnonzero(split==name) for name in ("train","validation","test")}
    for name,indices in ids.items():
        if set(y[indices])!={0,1}:
            raise ValueError(name+" must contain both classes")
    tr,va,te=(ids[name] for name in ("train","validation","test"))
    counts=np.bincount(y[tr],minlength=2)
    class_weight={i:len(tr)/(2*int(counts[i])) for i in (0,1)}
    features=image_features(x)
    baseline=make_pipeline(StandardScaler(),LogisticRegression(class_weight="balanced",random_state=42,max_iter=1000))
    baseline.fit(features[tr],y[tr])
    l=tf.keras.layers
    model=tf.keras.Sequential([l.Input((63,63,1)),l.RandomFlip("horizontal_and_vertical",seed=42),
        l.Conv2D(8,3,activation="relu"),l.MaxPooling2D(),
        l.Conv2D(16,3,activation="relu"),l.MaxPooling2D(),
        l.Conv2D(32,3,activation="relu"),l.GlobalAveragePooling2D(),
        l.Dropout(0.3),l.Dense(16,activation="relu"),l.Dense(1,activation="sigmoid")])
    model.compile(optimizer="adam",loss="binary_crossentropy",metrics=["accuracy"])
    options=tf.data.Options()
    options.threading.private_threadpool_size=2
    options.threading.max_intra_op_parallelism=2
    def dataset(indices,shuffle=False):
        d=tf.data.Dataset.from_tensor_slices((x[indices],y[indices]))
        if shuffle:
            d=d.shuffle(len(indices),seed=42)
        return d.batch(64).with_options(options)
    history=model.fit(dataset(tr,True),validation_data=dataset(va),epochs=args.epochs,
        class_weight=class_weight,callbacks=[tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",patience=3,restore_best_weights=True)],verbose=2)
    # Fixed model selection and thresholds; no held-out field test used in tuning.
    scores=model(x[te],training=False).numpy().ravel()
    base_scores=baseline.predict_proba(features[te])[:,1]
    def metrics(scores):
        pred=(scores>=0.5).astype(int)
        return dict(accuracy=float(accuracy_score(y[te],pred)),
            balanced_accuracy=float(balanced_accuracy_score(y[te],pred)),
            nominal_precision=float(precision_score(y[te],pred,zero_division=0)),
            nominal_recall=float(recall_score(y[te],pred,zero_division=0)),
            artifact_recall=float(recall_score(y[te],pred,pos_label=0,zero_division=0)),
            f1=float(f1_score(y[te],pred,zero_division=0)),roc_auc=float(roc_auc_score(y[te],scores)),
            average_precision=float(average_precision_score(y[te],scores)),
            confusion_matrix=confusion_matrix(y[te],pred,labels=[0,1]).tolist())
    report=dict(experiment="snad_nominal_artifact",seed=42,threshold=0.5,
        limitation="Separate field-held-out nominal/artifact pilot; not alert Real/Bogus accuracy.",
        tensorflow_version=tf.__version__,preprocessing="per-image median / MAD (std fallback), then asinh",
        epochs_completed=len(history.history["loss"]),best_epoch=int(np.argmin(history.history["val_loss"]))+1,
        cnn=metrics(scores),image_feature_logistic=metrics(base_scores),
        majority_accuracy=float(accuracy_score(y[te],np.full(len(te),np.argmax(counts)))),
        splits={name:dict(n=len(indices),class_counts=np.bincount(y[indices],minlength=2).tolist(),
            fields=sorted(int(v) for v in set(fields[indices]))) for name,indices in ids.items()},
        code_commit=os.environ.get("GITHUB_SHA","local"))
    (args.output/"metrics.json").write_text(json.dumps(report,indent=2))
    (args.output/"history.json").write_text(json.dumps(history.history,indent=2))
    (args.output/"split_manifest.json").write_text(json.dumps({name:[dict(object_id=str(objects[i]),
        field_id=int(fields[i]),group_id=str(groups[i])) for i in indices] for name,indices in ids.items()},indent=2))
    (args.output/"test_predictions.json").write_text(json.dumps([dict(object_id=str(objects[i]),field_id=int(fields[i]),
        label=int(y[i]),cnn_score=float(scores[j]),baseline_score=float(base_scores[j])) for j,i in enumerate(te)],indent=2))
    model.save(str(args.output/"model.keras"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for key in ("loss","val_loss"):
        axes[0].plot(range(1,len(history.history[key])+1),history.history[key],label=key)
    axes[0].set(xlabel="Epoch",ylabel="Binary cross entropy"); axes[0].legend()
    matrix=np.array(report["cnn"]["confusion_matrix"])
    axes[1].imshow(matrix,cmap="Blues")
    for (i,j),value in np.ndenumerate(matrix): axes[1].text(j,i,str(value),ha="center",va="center")
    axes[1].set(xticks=[0,1],yticks=[0,1],xticklabels=["Artifact","Nominal"],
        yticklabels=["Artifact","Nominal"],xlabel="Predicted",ylabel="True",title="Held-out fields")
    fig.tight_layout(); fig.savefig(args.output/"evaluation.png",dpi=140); plt.close(fig)
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
