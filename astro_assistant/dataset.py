"""Kaynağı doğrulanmış NPZ verisini doğrulama ve nesne bazında ayırma."""
import hashlib
import random


def group_split(object_ids, seed=42):
    groups = sorted(set(str(v) for v in object_ids))
    if len(groups) < 10:
        raise ValueError("Güvenilir bölme için en az 10 farklı object_id gerekli.")
    random.Random(seed).shuffle(groups)
    n_test = max(1, round(len(groups) * 0.15))
    n_val = max(1, round(len(groups) * 0.15))
    assignment = {g: "test" if i < n_test else "validation" if i < n_test+n_val else "train"
                  for i, g in enumerate(groups)}
    return {name: [i for i, g in enumerate(object_ids) if assignment[str(g)] == name]
            for name in ("train", "validation", "test")}


def normalize(images):
    import numpy as np
    images = np.asarray(images, dtype=np.float32)
    if not np.isfinite(images).all():
        raise ValueError("NaN/Inf görüntü pikselleri veri incelemesinde çözülmelidir.")
    # Independent L2 norm for science/reference/difference; no dataset-wide fit.
    norms = np.sqrt(np.sum(images.astype(np.float64)**2, axis=(1, 2), keepdims=True))
    if (norms == 0).any():
        raise ValueError("Tamamen boş kanal bulundu.")
    return (images / norms).astype(np.float32)


def load_dataset(path):
    import numpy as np
    with np.load(path, allow_pickle=False) as data:
        required = {"images", "labels", "object_ids", "alert_ids"}
        if not required <= set(data.files):
            raise ValueError("NPZ alanları eksik: " + str(required-set(data.files)))
        x, y = data["images"], data["labels"]
        objects, alerts = data["object_ids"], data["alert_ids"]
    if x.ndim != 4 or x.shape[1:] != (63, 63, 3):
        raise ValueError("Beklenen görüntü şekli: (N,63,63,3), science/reference/difference.")
    if y.shape != (len(x),) or objects.shape != y.shape or alerts.shape != y.shape:
        raise ValueError("Etiket ve kimlik boyutları görüntülerle uyuşmuyor.")
    if set(np.unique(y)) != {0, 1}:
        raise ValueError("Etiketler her iki sınıfı içermeli: 0=bogus, 1=real.")
    for ids in (objects, alerts):
        if ids.dtype.kind not in "US" or any(not str(v).strip() for v in ids):
            raise ValueError("Kimlikler boş olmayan Unicode/string dizileri olmalıdır.")
    if len(set(alerts.tolist())) != len(alerts):
        raise ValueError("Tekrarlanan alert_id bulundu.")
    hashes = [hashlib.sha256(image.tobytes()).hexdigest() for image in x]
    if len(set(hashes)) != len(hashes):
        raise ValueError("Birebir tekrarlanan görüntüler var; bölmeden önce inceleyin.")
    return normalize(x), y.astype("int32"), objects, alerts
