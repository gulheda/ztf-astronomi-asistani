import unittest
from astro_assistant.provenance import validate_provenance


class ProvenanceTests(unittest.TestCase):
    def record(self):
        return dict(source_url="https://example.org/synthetic-test-only", retrieved_at="2026-10-17",
            label_definition="synthetic test fixture", label_source="fixture", license="fixture",
            sha256="a"*64, label_kind="human_reviewed", labels_independent_of_model=True,
            label_review_reference="synthetic test only", is_demo=False)

    def test_complete_declaration(self):
        validate_provenance(self.record())

    def test_pseudo_labels_rejected(self):
        for key, value in (("label_kind", "model_pseudo_label"),
                           ("labels_independent_of_model", False), ("label_review_reference", ""),
                           ("sha256", "bad"), ("is_demo", True)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                record = self.record()
                record[key] = value
                validate_provenance(record)
