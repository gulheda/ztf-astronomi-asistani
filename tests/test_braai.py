import base64
import gzip
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from astro_assistant.braai import fetch_verified, make_triplet


class SourceTests(unittest.TestCase):
    def test_corrupt_cache_rejected_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "714287740515015072.json").write_bytes(b"corrupt")
            with patch("astro_assistant.braai.urlopen") as network:
                with self.assertRaises(ValueError):
                    fetch_verified("714287740515015072.json", directory)
                network.assert_not_called()

    def test_unknown_download_rejected(self):
        with tempfile.TemporaryDirectory() as directory, patch("astro_assistant.braai.urlopen") as network:
            with self.assertRaises(KeyError):
                fetch_verified("../../unexpected", directory)
            network.assert_not_called()


@unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("astropy"),
                     "NumPy and Astropy required")
class CutoutTests(unittest.TestCase):
    def alert(self, data):
        from astropy.io import fits
        stream = io.BytesIO()
        fits.PrimaryHDU(data).writeto(stream)
        encoded = base64.b64encode(gzip.compress(stream.getvalue())).decode()
        return {key: {"stampData": {"$binary": encoded}} for key in
                ("cutoutScience", "cutoutTemplate", "cutoutDifference")}

    def test_signed_pixels_normalized_and_padded(self):
        import numpy as np
        data = np.array([[1., -1.], [float("nan"), 2.]], dtype=np.float32)
        triplet, notes = make_triplet(self.alert(data))
        self.assertEqual(triplet.shape, (63, 63, 3))
        self.assertTrue((triplet[0,1,:] < 0).all())
        np.testing.assert_allclose(np.linalg.norm(triplet, axis=(0,1)), np.ones(3), rtol=1e-5)
        self.assertEqual(notes[0]["nan_replaced"], 1)

    def test_invalid_images_rejected(self):
        import numpy as np
        for data in (np.zeros((3,3)), np.ones((64,63)), np.full((3,3), np.inf)):
            with self.subTest(shape=data.shape), self.assertRaises(ValueError):
                make_triplet(self.alert(data))

    def test_oversized_gzip_rejected(self):
        alert = self.alert(__import__("numpy").ones((2,2)))
        alert["cutoutScience"]["stampData"]["$binary"] = base64.b64encode(gzip.compress(b"0"*1_000_001)).decode()
        with self.assertRaises(ValueError):
            make_triplet(alert)
