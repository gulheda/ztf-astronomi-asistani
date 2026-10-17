"""Bundled, published-model inference records for the Streamlit prototype."""
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

from .braai import BASE_URL, FILES, UPSTREAM_COMMIT


EXPERIMENT = "published_model_real_alert_inference"
DEFAULT_ARCHIVE = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "experiments"
    / "braai-2026-10-17"
    / "inference.json"
)


def _utc_timestamp(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Arşiv kaydında geçersiz alan: " + field)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Arşiv kaydında geçersiz zaman: " + field) from error
    if parsed.tzinfo is None:
        raise ValueError("Arşiv zamanları saat dilimi içermelidir: " + field)
    try:
        return parsed.astimezone(timezone.utc)
    except (OverflowError, ValueError) as error:
        raise ValueError("Arşiv kaydında geçersiz zaman: " + field) from error


def _number(value, field, minimum=None, maximum=None, nullable=False):
    if nullable and value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Arşiv kaydında geçersiz sayısal alan: " + field)
    if minimum is not None and value < minimum:
        raise ValueError("Arşiv kaydında aralık dışı alan: " + field)
    if maximum is not None and value > maximum:
        raise ValueError("Arşiv kaydında aralık dışı alan: " + field)


def _text(mapping, field, context="Arşiv kaydında"):
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s eksik alan: %s" % (context, field))
    return value


def load_archive(path=None):
    """Load and validate the repository's fixed real-alert inference bundle."""
    archive_path = Path(path) if path is not None else DEFAULT_ARCHIVE
    try:
        with archive_path.open("rb") as archive_file:
            payload = archive_file.read(1_000_001)
        if len(payload) > 1_000_000:
            raise ValueError("Gerçek ZTF arşivi 1 MB sınırını aşıyor.")
        bundle = json.loads(payload.decode("utf-8"))
    except ValueError as error:
        if str(error).startswith("Gerçek ZTF arşivi"):
            raise
        raise ValueError("Gerçek ZTF arşivi okunamadı: %s" % error) from error
    except OSError as error:
        raise ValueError("Gerçek ZTF arşivi okunamadı: %s" % error) from error

    if not isinstance(bundle, dict) or bundle.get("experiment") != EXPERIMENT:
        raise ValueError("Beklenmeyen veya eksik arşiv deney kimliği.")
    upstream_commit = _text(bundle, "upstream_commit", "Arşiv üst bilgisinde")
    if upstream_commit != UPSTREAM_COMMIT:
        raise ValueError("Arşiv upstream_commit sabitlenmiş kaynakla eşleşmiyor.")
    if bundle.get("training_performed") is not False:
        raise ValueError("Bu sabit arşiv eğitim çalışması içermez.")
    if bundle.get("independent_ground_truth_available") is not False:
        raise ValueError("Arşiv bağımsız doğruluk etiketi içerdiğini iddia ediyor.")
    if bundle.get("accuracy") is not None:
        raise ValueError("Bağımsız gerçek etiket olmadan doğruluk değeri kullanılamaz.")
    warning = _text(bundle, "warning", "Arşiv üst bilgisinde")

    sources = bundle.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Arşiv kaynak tanımları eksik.")
    expected_sources = {
        name: {"url": BASE_URL + relative, "bytes": byte_count, "sha256": digest}
        for name, (relative, byte_count, digest) in FILES.items()
    }
    if sources != expected_sources:
        raise ValueError("Arşiv kaynak tanımları sabitlenmiş braai kaynaklarıyla eşleşmiyor.")
    validated_sources = {}
    for source_name, descriptor in sources.items():
        if not isinstance(source_name, str) or not source_name.strip() or not isinstance(descriptor, dict):
            raise ValueError("Geçersiz arşiv kaynak tanımı.")
        url = _text(descriptor, "url", "Arşiv kaynak tanımında")
        byte_count = descriptor.get("bytes")
        digest = descriptor.get("sha256")
        if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
            raise ValueError("Arşiv kaynak tanımında geçersiz bytes.")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Arşiv kaynak tanımında geçersiz sha256.")
        validated_sources[source_name] = dict(descriptor)

    raw_records = bundle.get("records")
    if not isinstance(raw_records, list) or not raw_records:
        raise ValueError("Gerçek ZTF arşivinde kayıt bulunamadı.")
    records = []
    observed_times = []
    alert_ids = set()
    identities = set()
    model_versions = set()
    for raw_record in raw_records:
        if not isinstance(raw_record, dict):
            raise ValueError("Arşiv kayıtları nesne olmalıdır.")
        record = dict(raw_record)
        alert_id = _text(record, "alert_id")
        object_id = _text(record, "object_id")
        if alert_id in alert_ids or (alert_id, object_id) in identities:
            raise ValueError("Arşivde yinelenen uyarı kimliği: " + alert_id)
        alert_ids.add(alert_id)
        identities.add((alert_id, object_id))

        observed_times.append(_utc_timestamp(record.get("observed_at"), "observed_at"))
        _number(record.get("ra"), "ra", 0, 360)
        if record["ra"] == 360:
            raise ValueError("Arşiv kaydında aralık dışı alan: ra")
        _number(record.get("dec"), "dec", -90, 90)
        _number(record.get("magnitude"), "magnitude", nullable=True)
        _number(record.get("real_score"), "real_score", 0, 1)
        if record.get("band") not in ("g", "r", "i"):
            raise ValueError("Arşiv kaydında geçersiz band.")
        if type(record.get("is_demo")) is not int or record["is_demo"] != 0:
            raise ValueError("Gerçek arşiv kayıtlarında is_demo tam sayı 0 olmalıdır.")
        if record.get("kind") is not None or record.get("kind_source") is not None:
            raise ValueError("Real/Bogus skoru astrofiziksel olay türü etiketi değildir.")

        _number(record.get("upstream_rb"), "upstream_rb", 0, 1)
        preprocessing = record.get("preprocessing")
        if not isinstance(preprocessing, list) or not preprocessing:
            raise ValueError("Arşiv kaydında preprocessing tanımı eksik.")
        for channel in preprocessing:
            if not isinstance(channel, dict):
                raise ValueError("Arşiv kaydında geçersiz preprocessing tanımı.")
            _text(channel, "channel", "Preprocessing tanımında")
            shape = channel.get("original_shape")
            if (not isinstance(shape, list) or len(shape) != 2 or
                    any(type(size) is not int or size <= 0 for size in shape)):
                raise ValueError("Preprocessing tanımında geçersiz original_shape.")
            nan_replaced = channel.get("nan_replaced")
            if type(nan_replaced) is not int or nan_replaced < 0:
                raise ValueError("Preprocessing tanımında geçersiz nan_replaced.")

        model_version = _text(record, "model_version")
        source = _text(record, "source")
        if model_version != "braai_d6_m9@" + UPSTREAM_COMMIT:
            raise ValueError("Kayıt model sürümü sabitlenmiş modelle eşleşmiyor.")
        source_name = alert_id + ".json"
        if source_name not in FILES or source != BASE_URL + FILES[source_name][0]:
            raise ValueError("Kayıt kaynağı sabitlenmiş uyarı kaynağıyla eşleşmiyor.")
        model_versions.add(model_version)
        records.append(record)

    expected_alert_ids = {name[:-5] for name in FILES if name.endswith(".json")}
    if alert_ids != expected_alert_ids:
        raise ValueError("Arşiv sabitlenmiş iki ZTF uyarısını eksiksiz içermelidir.")

    reference_time = max(observed_times)
    query = bundle.get("query")
    if not isinstance(query, dict):
        raise ValueError("Arşiv sorgu tanımı eksik.")
    stated_reference = _utc_timestamp(query.get("reference_time_utc"), "query.reference_time_utc")
    if stated_reference != reference_time:
        raise ValueError("Arşiv referans zamanı en yeni kayıtla eşleşmiyor.")

    provenance = {
        "experiment": EXPERIMENT,
        "upstream_commit": upstream_commit,
        "model_versions": sorted(model_versions),
        "sources": validated_sources,
        "record_count": len(records),
        "independent_ground_truth_available": False,
        "accuracy": None,
        "warning": warning,
    }
    return {
        "reference_time": reference_time,
        "records": records,
        "provenance": provenance,
    }
