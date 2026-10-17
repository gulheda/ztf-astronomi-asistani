"""SNAD preparation regression checks using only synthetic data."""
import hashlib
import io
from unittest.mock import patch
from zipfile import ZipFile
import importlib.util
from pathlib import Path
import tempfile
import unittest


@unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("scipy"), "NumPy/SciPy required")
class SnadDatasetTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        from astro_assistant import snad_dataset
        self.np = np
        self.module = snad_dataset

    def test_source_integrity_rejects_wrong_length_or_digest(self):
        payload = b"synthetic source archive"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.zip"
            path.write_bytes(payload)
            digest = hashlib.md5(payload).hexdigest()
            self.assertEqual(self.module.verify_source(path, len(payload), digest), payload)
            for size, checksum in ((len(payload) - 1, digest), (len(payload), "0" * 32)):
                with self.subTest(size=size, checksum=checksum), self.assertRaises(ValueError):
                    self.module.verify_source(path, size, checksum)

    def test_normalize_finite_preserves_relative_contrast_without_mutation(self):
        np = self.np
        image = np.arange(63 * 63, dtype="float32").reshape(63, 63)
        before = image.copy()
        actual = self.module.normalize_image(image)
        np.testing.assert_array_equal(image, before)
        self.assertEqual(actual.dtype, np.float32)
        self.assertTrue(np.isfinite(actual).all())
        flat = actual.reshape(-1)
        self.assertGreater(float(flat[-1]), float(flat[0]))
        self.assertAlmostEqual(float(flat[200] - flat[100]), float(flat[300] - flat[200]), places=5)

    def test_normalize_rejects_invalid_images(self):
        np = self.np
        for value in (np.nan, np.inf, -np.inf):
            image = np.arange(3969, dtype="float32").reshape(63, 63)
            image[0, 0] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.module.normalize_image(image)
        with self.assertRaises(ValueError):
            self.module.normalize_image(np.ones((63, 63), dtype="float32"))

    def fixture(self):
        np = self.np
        # Twenty independent fields, each with both labels.
        objects = np.array(["synthetic-%d" % i for i in range(40)])
        fields = np.repeat(np.arange(20), 2)
        ra = np.arange(40, dtype=float) * 5.0
        dec = np.zeros(40)
        labels = np.tile([0, 1], 20)
        return objects, fields, ra, dec, labels

    def test_split_complete_and_keeps_fields_together(self):
        np = self.np
        args = self.fixture()
        split, groups = self.module.make_splits(*args)
        self.assertEqual(len(split), 40)
        self.assertEqual(set(split), {"train", "validation", "test"})
        for field in np.unique(args[1]):
            self.assertEqual(len(set(split[args[1] == field])), 1)
        repeated, repeated_groups = self.module.make_splits(*args)
        np.testing.assert_array_equal(split, repeated)
        np.testing.assert_array_equal(groups, repeated_groups)

    def test_oid_and_transitive_coordinate_matches_cross_field_stay_together(self):
        np = self.np
        objects, fields, ra, dec, labels = self.fixture()
        objects[2] = objects[0]
        # 0--2 linked by OID; 2--4 by sky position; 4--5 by field.
        ra[2], ra[4] = 359.99995, 0.00005
        split, groups = self.module.make_splits(objects, fields, ra, dec, labels)
        self.assertEqual(len(set(groups[[0, 1, 2, 3, 4, 5]])), 1)
        self.assertEqual(len(set(split[[0, 1, 2, 3, 4, 5]])), 1)


@unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("astropy"), "NumPy/Astropy required")
class SnadArchiveTests(unittest.TestCase):
    def archive(self, path, label, duplicate_image=False, invalid=False):
        import numpy as np
        from astropy.io import fits
        prefix = ("Artefacts", "Nominals")[label]
        child = io.BytesIO()
        with ZipFile(child, "w") as archive:
            for i in range(20):
                image = np.random.default_rng(100 + i + (0 if duplicate_image else label * 100)).normal(size=(63, 63)).astype("float32")
                if invalid and i == 0:
                    image[0, 0] = np.nan
                hdu = fits.PrimaryHDU(image)
                for key, value in {"OID": str(label * 100 + i), "FIELDID": i + 1,
                                   "OIDRA": i * 5.0 + label, "OIDDEC": 0.0,
                                   "OBSJD": 2459000.5, "FILTERID": 2}.items():
                    hdu.header[key] = value
                data = io.BytesIO()
                hdu.writeto(data)
                # A hostile member path must remain in memory.
                archive.writestr("../../fixture-%d.fits" % i, data.getvalue())
        with ZipFile(path, "w") as archive:
            archive.writestr(prefix + "/63x63/fits.zip", child.getvalue())

    def sources(self, directory, duplicate=False, invalid=False):
        specs = {}
        for label, name in enumerate(("Artefacts.zip", "Nominals.zip")):
            path = Path(directory) / name
            self.archive(path, label, duplicate_image=duplicate, invalid=invalid and label == 0)
            payload = path.read_bytes()
            specs[str(label)] = (name, len(payload), hashlib.md5(payload).hexdigest())
        return specs

    def test_duplicate_pixels_across_labels_fail_closed(self):
        from astro_assistant import snad_dataset as module
        with tempfile.TemporaryDirectory() as directory:
            specs = self.sources(directory, duplicate=True)
            output = Path(directory) / "output"
            with patch.object(module, "SOURCES", specs), self.assertRaisesRegex(ValueError, "duplicate"):
                module.prepare(directory, output)
            self.assertFalse((output / "dataset.npz").exists())
            self.assertTrue((output / "audit.json").exists())

    def test_nonfinite_input_fails_closed_with_audit(self):
        from astro_assistant import snad_dataset as module
        with tempfile.TemporaryDirectory() as directory:
            specs = self.sources(directory, invalid=True)
            output = Path(directory) / "output"
            with patch.object(module, "SOURCES", specs), self.assertRaisesRegex(ValueError, "Quality control"):
                module.prepare(directory, output)
            self.assertFalse((output / "dataset.npz").exists())

    def test_valid_preparation_does_not_extract_paths(self):
        import numpy as np
        from astro_assistant import snad_dataset as module
        with tempfile.TemporaryDirectory() as directory:
            specs = self.sources(directory)
            output = Path(directory) / "output"
            with patch.object(module, "SOURCES", specs):
                result = module.prepare(directory, output)
            with np.load(result, allow_pickle=False) as dataset:
                self.assertEqual(dataset["images"].shape, (40, 63, 63, 1))
                self.assertTrue(np.isfinite(dataset["images"]).all())
                self.assertEqual(set(dataset["split"]), {"train", "validation", "test"})
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ["Artefacts.zip", "Nominals.zip", "output"])


if __name__ == "__main__":
    unittest.main()
