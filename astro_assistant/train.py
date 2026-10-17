"""Veri sözleşmesine uyan gerçek veri geldikten sonra Colab'da çalıştırılacak eğitim iskeleti."""
import argparse
import hashlib
import json
from pathlib import Path
from .dataset import load_dataset, group_split
from .provenance import validate_provenance


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Yeni bir deney klasörü")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    provenance = json.loads(args.provenance.read_text())
    try:
        validate_provenance(provenance)
    except ValueError as error:
        parser.error(str(error))
    digest = hashlib.sha256()
    with args.dataset.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != provenance["sha256"]:
        parser.error("Veri SHA256 özeti kaynak kaydıyla uyuşmuyor.")
    if args.epochs < 1:
        parser.error("epochs pozitif olmalı.")
    import numpy as np
    import tensorflow as tf
    from sklearn.metrics import (accuracy_score, balanced_accuracy_score, precision_score,
        recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix)
    tf.keras.utils.set_random_seed(args.seed)
    x, y, objects, alerts = load_dataset(args.dataset)
    split = group_split(objects, args.seed)
    for name, indices in split.items():
        if set(y[indices]) != {0, 1}:
            raise ValueError(name + " her iki sınıfı içermiyor; grup dağılımını inceleyin.")
    args.output.mkdir(parents=True, exist_ok=False)
    tr, va, te = (split[k] for k in ("train", "validation", "test"))
    layers = tf.keras.layers
    model = tf.keras.Sequential([
        layers.Input(shape=(63, 63, 3)), layers.RandomFlip("horizontal_and_vertical", seed=args.seed),
        layers.Conv2D(16, 3, activation="relu"), layers.MaxPooling2D(),
        layers.Conv2D(32, 3, activation="relu"), layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation="relu"), layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3), layers.Dense(32, activation="relu"), layers.Dense(1, activation="sigmoid")])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    counts = np.bincount(y[tr], minlength=2)
    weights = {i: len(tr)/(2*int(counts[i])) for i in (0, 1)}
    history = model.fit(x[tr], y[tr], validation_data=(x[va], y[va]), epochs=args.epochs,
        batch_size=64, class_weight=weights,
        callbacks=[tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)])
    # Fixed threshold established before looking at held-out test results.
    scores = model.predict(x[te], verbose=0).ravel()
    pred = (scores >= 0.5).astype(int)
    metrics = dict(accuracy=accuracy_score(y[te], pred),
        balanced_accuracy=balanced_accuracy_score(y[te], pred),
        precision=precision_score(y[te], pred, zero_division=0),
        recall=recall_score(y[te], pred, zero_division=0),
        f1=f1_score(y[te], pred, zero_division=0), roc_auc=roc_auc_score(y[te], scores),
        average_precision=average_precision_score(y[te], scores),
        confusion_matrix=confusion_matrix(y[te], pred, labels=[0, 1]).tolist(),
        majority_baseline_accuracy=accuracy_score(y[te], np.full(len(te), int(np.argmax(counts)))),
        threshold=0.5, seed=args.seed, tensorflow_version=tf.__version__,
        split_counts={k: len(v) for k, v in split.items()},
        class_counts={k: np.bincount(y[v], minlength=2).tolist() for k,v in split.items()})
    model.save(str(args.output / "model.keras"))
    (args.output / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (args.output / "history.json").write_text(json.dumps(history.history, indent=2))
    (args.output / "provenance.json").write_text(json.dumps(provenance, indent=2))
    (args.output / "split.json").write_text(json.dumps({k: alerts[v].tolist() for k,v in split.items()}))
    np.savez_compressed(args.output / "test_predictions.npz", alert_ids=alerts[te], labels=y[te], scores=scores)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
