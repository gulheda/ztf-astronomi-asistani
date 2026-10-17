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

    def test_real_archive_default_threshold_and_switch_back_to_demo(self):
        app = self.start()
        # The real archive is opt-in so existing demo behavior remains the default.
        self.assertEqual(len(app.dataframe), 1)
        selectors = [item for item in app.selectbox]
        real_selector = next(item for item in selectors if "veri" in item.label.lower() or
                             "kaynak" in item.label.lower() or "mod" in item.label.lower())
        real_selector.select("Gerçek ZTF arşivi").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.dataframe), 1)
        rows = app.dataframe[0].value
        self.assertEqual(list(rows["alert_id"]), ["714287740515015072"])
        self.assertTrue(rows["source"].iloc[0].startswith("https://raw.githubusercontent.com/"))
        self.assertIn("braai_d6_m9", rows["model_version"].iloc[0])
        if "kind" in rows.columns:
            self.assertTrue(rows["kind"].isna().all())
        if "kind_source" in rows.columns:
            self.assertTrue(rows["kind_source"].isna().all())

        # Lowering the score cutoff reveals both dated examples.
        threshold = next(item for item in app.slider if "eşik" in item.label.lower())
        threshold.set_value(0.0).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(set(app.dataframe[0].value["alert_id"]),
                         {"714287740515015072", "893215910715010007"})

        real_selector.select("Demo").run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(all(str(value).startswith("DEMO-")
                            for value in app.dataframe[0].value["alert_id"]))
