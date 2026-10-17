"""Synthetic archive tests; no external data needed."""
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
from astro_assistant.snad_audit import inspect_archive


@unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("astropy"),"NumPy/Astropy required")
class ArchiveTests(unittest.TestCase):
    def test_sample_reads_fits_without_extracting_paths(self):
        import numpy as np
        from astropy.io import fits
        stream=io.BytesIO()
        fits.PrimaryHDU(np.ones((63,63),dtype="float32")).writeto(stream)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"synthetic.zip"
            with ZipFile(path,"w") as archive:
                archive.writestr("../../synthetic.fits",stream.getvalue())
            report=inspect_archive(path)
            self.assertEqual(report["fits_count"],1)
            self.assertEqual(report["samples"][0]["shape"],[63,63])
            self.assertEqual(list(Path(directory).iterdir()),[path])

    def test_missing_fits_fails_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"synthetic.zip"
            with ZipFile(path,"w") as archive:
                archive.writestr("readme.txt","synthetic fixture")
            with self.assertRaises(ValueError):
                inspect_archive(path)
