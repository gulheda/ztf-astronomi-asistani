"""Pinned, published braai d6_m9 inference; no training or accuracy claims.

Architecture and preprocessing adapted from Dmitry Duev's MIT-licensed braai.
See THIRD_PARTY_NOTICES.md. Only fixed upstream public examples are downloaded.
"""
import argparse
import base64
import gzip
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen

UPSTREAM_COMMIT = "9fb2259542ec4b0a7dfa485012a23dc15a3f4ce8"
BASE_URL = "https://raw.githubusercontent.com/dmitryduev/braai/" + UPSTREAM_COMMIT + "/"
FILES = {
    "714287740515015072.json": ("nb/714287740515015072.json", 80380,
        "f4192eaaa22f747af573886dfd5d4dd65ac60554502b7c79bef19f59de87c869"),
    "893215910715010007.json": ("nb/893215910715010007.json", 156880,
        "0ef195d369cd4cb0f4d549bc4c535b784ef90b08f75f526c21fd8551dcad36a3"),
    "braai_d6_m9.weights.h5": ("models/braai_d6_m9.weights.h5", 1277944,
        "de0d198246d1a30effecf3bdd83ada0b8218ccdfaf7d5fdaf2de0af061413b2f"),
}


def fetch_verified(name, cache):
    relative, expected_size, expected_sha = FILES[name]
    path = Path(cache) / name
    if path.exists():
        if path.stat().st_size != expected_size:
            raise ValueError("Cached source has wrong size: " + name)
        payload = path.read_bytes()
    else:
        url = BASE_URL + relative
        with urlopen(url, timeout=30) as response:
            if response.geturl() != url:
                raise ValueError("Unexpected source redirect")
            payload = response.read(expected_size + 1)
    if len(payload) != expected_size or hashlib.sha256(payload).hexdigest() != expected_sha:
        raise ValueError("Source size/SHA256 mismatch: " + name)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(payload)
    return path


def make_triplet(alert):
    import numpy as np
    from astropy.io import fits
    channels, diagnostics = [], []
    for key in ("cutoutScience", "cutoutTemplate", "cutoutDifference"):
        encoded = alert[key]["stampData"]["$binary"]
        if isinstance(encoded, dict):
            encoded = encoded["base64"]
        if not isinstance(encoded, str) or len(encoded) > 1_000_000:
            raise ValueError("Invalid or oversized encoded cutout")
        compressed = base64.b64decode("".join(encoded.split()), validate=True)
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
            payload = stream.read(1_000_001)
        if len(payload) > 1_000_000:
            raise ValueError("Decompressed cutout exceeds limit")
        with fits.open(io.BytesIO(payload), memmap=False, lazy_load_hdus=True) as hdus:
            h = hdus[0].header
            if h.get("NAXIS") != 2 or not all(1 <= h.get(k, 0) <= 63 for k in ("NAXIS1", "NAXIS2")):
                raise ValueError("Expected 2D cutout no larger than 63 x 63")
            data = np.array(hdus[0].data, dtype=np.float32, copy=True)
        if np.isinf(data).any():
            raise ValueError("Infinite image pixels")
        nan_count = int(np.isnan(data).sum())
        data[np.isnan(data)] = 0.0
        norm = np.linalg.norm(data)
        if not np.isfinite(norm) or norm == 0:
            raise ValueError("Invalid cutout norm")
        # d6_m9 uses global per-channel L2; old d6_m7 used row-wise norms.
        data /= norm
        diagnostics.append(dict(channel=key, original_shape=list(data.shape), nan_replaced=nan_count))
        data = np.pad(data, ((0, 63-data.shape[0]), (0, 63-data.shape[1])), constant_values=1e-9)
        channels.append(data)
    return np.stack(channels, axis=-1), diagnostics


def build_model(weights):
    import tensorflow as tf
    l = tf.keras.layers
    model = tf.keras.Sequential([
        l.Input(shape=(63, 63, 3)),
        l.Conv2D(16, 3, activation="relu", name="conv1"),
        l.Conv2D(16, 3, activation="relu", name="conv2"),
        l.MaxPooling2D(2), l.Dropout(0.25),
        l.Conv2D(32, 3, activation="relu", name="conv3"),
        l.Conv2D(32, 3, activation="relu", name="conv4"),
        l.MaxPooling2D(4), l.Dropout(0.25), l.Flatten(),
        l.Dense(256, activation="relu", name="fc_1"), l.Dropout(0.5),
        l.Dense(1, activation="sigmoid", name="fc_out")])
    # Upstream's legacy HDF5 uses a name now reserved for Keras' new format.
    # A verified copy with plain .h5 selects the legacy weight reader, not a
    # serialized model loader. No architecture/custom object is deserialized.
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        legacy = Path(directory) / "braai_legacy.h5"
        shutil.copyfile(weights, legacy)
        model.load_weights(str(legacy))
    return model


def run(cache, output):
    import numpy as np
    import tensorflow as tf
    from astropy.time import Time
    from datetime import timezone
    from .core import connect, insert_alerts, query_alerts, parse_query, utc
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    files = {name: fetch_verified(name, cache) for name in FILES}
    tf.keras.utils.set_random_seed(42)
    tf.config.threading.set_intra_op_parallelism_threads(2)
    tf.config.threading.set_inter_op_parallelism_threads(2)
    model = build_model(files["braai_d6_m9.weights.h5"])
    results, images = [], []
    for name in FILES:
        if not name.endswith(".json"):
            continue
        alert = json.loads(files[name].read_text())
        candidate = alert["candidate"]
        triplet, diagnostic = make_triplet(alert)
        score = float(model(triplet[None, ...], training=False).numpy()[0, 0])
        if not np.isfinite(score) or not 0 <= score <= 1:
            raise ValueError("Invalid model output")
        images.append(triplet)
        results.append(dict(alert_id=str(alert["candid"]), object_id=alert["objectId"],
            observed_at=Time(candidate["jd"], format="jd", scale="utc").to_datetime(timezone=timezone.utc).isoformat(),
            ra=candidate["ra"], dec=candidate["dec"], magnitude=candidate.get("magpsf"),
            band={1:"g", 2:"r", 3:"i"}[candidate["fid"]], real_score=score,
            model_version="braai_d6_m9@" + UPSTREAM_COMMIT,
            source=BASE_URL + FILES[name][0], kind=None, kind_source=None, is_demo=0,
            upstream_rb=candidate.get("rb"), preprocessing=diagnostic))
    db = connect(str(output / "alerts.sqlite"))
    try:
        insert_alerts(db, results)
        reference = max(utc(r["observed_at"]) for r in results)
        queried = query_alerts(db, parse_query("Son 365 gündeki olaylar"), reference, threshold=0.5)
    finally:
        db.close()
    report = dict(experiment="published_model_real_alert_inference", training_performed=False,
        independent_ground_truth_available=False, accuracy=None,
        warning="Two upstream examples are not a representative or independent test set. No accuracy claim.",
        upstream_commit=UPSTREAM_COMMIT, tensorflow_version=tf.__version__, numpy_version=np.__version__,
        sources={name: dict(url=BASE_URL+v[0], bytes=v[1], sha256=v[2]) for name,v in FILES.items()},
        records=results, query=dict(text="Son 365 gündeki olaylar", reference_time_utc=reference.isoformat(),
            threshold=0.5, result_alert_ids=[r["alert_id"] for r in queried]))
    (output / "inference.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(len(images), 3, figsize=(10, 7), squeeze=False)
    for i, triplet in enumerate(images):
        for j, title in enumerate(("Science", "Reference", "Difference")):
            axes[i,j].imshow(triplet[:,:,j], cmap="gray", origin="upper")
            axes[i,j].set_title(title)
            axes[i,j].set_xticks([]); axes[i,j].set_yticks([])
        axes[i,0].set_ylabel(results[i]["object_id"] + "\nscore=%.6f" % results[i]["real_score"])
    fig.suptitle("Published braai d6_m9 on two real ZTF alerts\nInference check; no independent labels or accuracy estimate")
    fig.tight_layout()
    fig.savefig(output / "real_alert_triplets.png", dpi=140)
    plt.close(fig)
    print(json.dumps(report, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("data/raw/braai"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.cache, args.output)


if __name__ == "__main__":
    main()
