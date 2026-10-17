"""Gerçek ZTF örnek arşivinin paket sözleşmesi ve güvenli yükleme sınırları."""
import copy
import json
import math
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from astro_assistant.archive import load_archive


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/experiments/braai-2026-10-17/inference.json"


def fixture_data():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class ArchiveTests(unittest.TestCase):
    def test_default_archive_has_the_two_known_real_alerts(self):
        archive = load_archive()
        self.assertEqual(archive["reference_time"], datetime(2019, 6, 13, 5, 10, 55, 4145, tzinfo=timezone.utc))
        self.assertEqual([row["alert_id"] for row in archive["records"]],
                         ["714287740515015072", "893215910715010007"])
        self.assertTrue(all(row["is_demo"] == 0 for row in archive["records"]))
        self.assertTrue(all(row["kind"] is None and row["kind_source"] is None
                            for row in archive["records"]))
        self.assertEqual(archive["provenance"]["upstream_commit"],
                         "9fb2259542ec4b0a7dfa485012a23dc15a3f4ce8")

    def test_fixture_path_loading_validates_reference_and_future_rows(self):
        data = fixture_data()
        data["records"][0]["observed_at"] = "2019-06-14T00:00:00Z"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inference.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_archive(path)

    def test_duplicate_alert_ids_are_rejected(self):
        data = fixture_data()
        data["records"][1]["alert_id"] = data["records"][0]["alert_id"]
        self.assert_invalid(data)

    def test_nonfinite_scores_and_untrusted_provenance_are_rejected(self):
        for score in (float("nan"), float("inf"), -0.01, 1.01):
            data = fixture_data()
            data["records"][0]["real_score"] = score
            with self.subTest(score=score):
                self.assert_invalid(data)
        data = fixture_data()
        data["records"][0]["source"] = "synthetic-demo"
        self.assert_invalid(data)

    def test_demo_or_derived_class_labels_cannot_enter_real_archive(self):
        for change in ({"is_demo": 1}, {"kind": "supernova", "kind_source": "synthetic-demo"},
                       {"kind": "asteroid", "kind_source": None}):
            data = fixture_data()
            data["records"][0].update(change)
            with self.subTest(change=change):
                self.assert_invalid(data)

    def test_archive_has_no_accuracy_or_ground_truth_claim(self):
        archive = load_archive()
        self.assertIsNone(archive["provenance"].get("accuracy"))
        self.assertFalse(archive["provenance"].get("independent_ground_truth_available", False))

    def test_coherently_changed_upstream_commit_is_rejected(self):
        data = fixture_data()
        replacement = "a" * 40
        data["upstream_commit"] = replacement
        data["records"][0]["model_version"] = data["records"][0]["model_version"].replace(
            "9fb2259542ec4b0a7dfa485012a23dc15a3f4ce8", replacement)
        for descriptor in data["sources"].values():
            descriptor["url"] = descriptor["url"].replace(
                "9fb2259542ec4b0a7dfa485012a23dc15a3f4ce8", replacement)
        for record in data["records"]:
            record["source"] = record["source"].replace(
                "9fb2259542ec4b0a7dfa485012a23dc15a3f4ce8", replacement)
        self.assert_invalid(data)

    def test_archive_cannot_drop_a_required_known_record(self):
        data = fixture_data()
        data["records"] = [next(row for row in data["records"]
                                 if row["alert_id"] == "893215910715010007")]
        self.assert_invalid(data)

    def test_invalid_utf8_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inference.json"
            path.write_bytes(b"\xff\xfe\xfa")
            with self.assertRaises(ValueError):
                load_archive(path)

    def test_extreme_timestamp_offset_overflow_is_rejected(self):
        data = fixture_data()
        data["records"][0]["observed_at"] = "2019-06-13T05:10:55+24:00"
        self.assert_invalid(data)

    def assert_invalid(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inference.json"
            path.write_text(json.dumps(data, allow_nan=True), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_archive(path)


if __name__ == "__main__":
    unittest.main()
