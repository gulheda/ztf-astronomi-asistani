"""Veri sözleşmesi testleri; tüm görüntü ve kimlikler açıkça sentetiktir."""
import importlib.util
from pathlib import Path
import random
import tempfile
import unittest

from astro_assistant.dataset import group_split, load_dataset, normalize


class GroupSplitTests(unittest.TestCase):
    def test_too_few_distinct_objects_rejected(self):
        for ids in ([], ["synthetic"] * 20, [str(i) for i in range(9)]):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                group_split(ids)

    def test_partition_has_every_index_exactly_once(self):
        ids = ["synthetic-%d" % i for i in range(31) for _ in range(i % 4 + 1)]
        split = group_split(ids)
        self.assertEqual(set(split), {"train", "validation", "test"})
        self.assertTrue(all(split.values()))
        indices = [i for part in split.values() for i in part]
        self.assertEqual(sorted(indices), list(range(len(ids))))
        groups = {name: {ids[i] for i in part} for name, part in split.items()}
        self.assertFalse(groups["train"] & groups["test"])
        self.assertFalse(groups["train"] & groups["validation"])
        self.assertFalse(groups["test"] & groups["validation"])

    def test_assignment_independent_of_input_order(self):
        ids = ["synthetic-%d" % i for i in range(40)]
        reverse = list(reversed(ids))
        first, second = group_split(ids), group_split(reverse)
        for name in first:
            self.assertEqual({ids[i] for i in first[name]}, {reverse[i] for i in second[name]})

    def test_local_seed_does_not_modify_global_rng(self):
        before = random.getstate()
        group_split(["synthetic-%d" % i for i in range(40)])
        self.assertEqual(random.getstate(), before)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy kurulu değil")
class DatasetTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "synthetic_fixture.npz"
        self.data = {
            "images": np.random.default_rng(42).normal(size=(4, 63, 63, 3)).astype("float32"),
            "labels": np.array([0, 1, 0, 1]),
            "object_ids": np.array(["synthetic-object-%d" % i for i in range(4)]),
            "alert_ids": np.array(["synthetic-alert-%d" % i for i in range(4)]),
        }

    def load(self):
        self.np.savez(self.path, **self.data)
        return load_dataset(self.path)

    def test_valid_fixture_preserves_labels_ids_and_normalizes_channels(self):
        images, labels, objects, alerts = self.load()
        self.assertEqual(images.shape, (4, 63, 63, 3))
        self.assertEqual(images.dtype, self.np.float32)
        self.assertEqual(labels.dtype, self.np.int32)
        for actual, name in ((labels, "labels"), (objects, "object_ids"), (alerts, "alert_ids")):
            self.np.testing.assert_array_equal(actual, self.data[name])
        self.np.testing.assert_allclose(self.np.sum(images.astype("float64") ** 2, axis=(1, 2)), 1, rtol=1e-6)

    def test_normalization_is_per_image_channel_and_does_not_mutate_input(self):
        original = self.data["images"].copy()
        batch = normalize(original)
        single = normalize(original[:1])
        self.np.testing.assert_array_equal(batch[:1], single)
        self.np.testing.assert_array_equal(original, self.data["images"])
        self.np.testing.assert_array_equal(self.np.sign(batch), self.np.sign(original))

    def test_nonfinite_pixels_rejected(self):
        for value in (self.np.nan, self.np.inf, -self.np.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                images = self.data["images"].copy()
                images[0, 0, 0, 0] = value
                normalize(images)

    def test_zero_channel_rejected(self):
        self.data["images"][0, :, :, 1] = 0
        with self.assertRaises(ValueError):
            self.load()

    def test_missing_fields_rejected(self):
        for name in list(self.data):
            removed = self.data.pop(name)
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.load()
            self.data[name] = removed

    def test_incorrect_image_shape_rejected(self):
        self.data["images"] = self.data["images"][:, :62]
        with self.assertRaises(ValueError):
            self.load()

    def test_mismatched_lengths_rejected(self):
        for name in ("labels", "object_ids", "alert_ids"):
            original = self.data[name]
            self.data[name] = original[:-1]
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.load()
            self.data[name] = original

    def test_single_class_and_nonbinary_labels_rejected(self):
        for labels in ([0, 0, 0, 0], [1, 1, 1, 1], [0, 1, 2, 1]):
            self.data["labels"] = self.np.array(labels)
            with self.subTest(labels=labels), self.assertRaises(ValueError):
                self.load()

    def test_empty_unicode_ids_rejected(self):
        for name in ("object_ids", "alert_ids"):
            original = self.data[name].copy()
            for value in ("", "   "):
                self.data[name][0] = value
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    self.load()
            self.data[name] = original

    def test_numeric_ids_rejected(self):
        self.data["object_ids"] = self.np.arange(4)
        with self.assertRaises(ValueError):
            self.load()

    def test_bytes_ids_rejected_even_when_nonempty(self):
        for name in ("object_ids", "alert_ids"):
            original = self.data[name]
            for value in (b"", b"   ", b"obj"):
                self.data[name] = self.np.array([value, b"synthetic-1", b"synthetic-2", b"synthetic-3"])
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    self.load()
            self.data[name] = original

    def test_pickled_object_arrays_rejected(self):
        self.data["object_ids"] = self.data["object_ids"].astype(object)
        with self.assertRaises(ValueError):
            self.load()

    def test_duplicate_alert_ids_rejected(self):
        self.data["alert_ids"][1] = self.data["alert_ids"][0]
        with self.assertRaises(ValueError):
            self.load()

    def test_duplicate_images_rejected(self):
        self.data["images"][1] = self.data["images"][0]
        with self.assertRaises(ValueError):
            self.load()


if __name__ == "__main__":
    unittest.main()
