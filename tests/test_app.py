"""Streamlit çalışma testi; tarayıcıda görsel incelemenin yerine geçmez."""
import importlib.util
import unittest
from pathlib import Path


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit kurulu değil")
class InterfaceTests(unittest.TestCase):
    def start(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)

    def test_demo_query_renders_results(self):
        app = self.start()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("DEMO", app.warning[0].value)
        self.assertEqual(len(app.dataframe), 1)
        self.assertGreater(len(app.dataframe[0].value), 0)

    def test_unsupported_query_shows_error(self):
        app = self.start()
        app.text_input[0].set_value("Mars hava durumu")
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 1)
        self.assertEqual(len(app.dataframe), 0)
