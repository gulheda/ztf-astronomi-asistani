"""Fail closed before a supervised evaluation is presented as independent."""


def validate_provenance(record):
    for field in ("source_url", "retrieved_at", "label_definition", "label_source", "license", "sha256",
                  "label_review_reference"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError("Kaynak kaydında eksik alan: " + field)
    if record.get("is_demo") is not False:
        raise ValueError("Gerçek veri için is_demo açıkça false olmalı.")
    if record.get("label_kind") != "human_reviewed" or record.get("labels_independent_of_model") is not True:
        raise ValueError("Standart test için modelden bağımsız, insan tarafından incelenmiş etiketler gerekli.")
    checksum = record["sha256"]
    if len(checksum) != 64 or any(c not in "0123456789abcdef" for c in checksum):
        raise ValueError("Geçersiz SHA256 özeti.")
