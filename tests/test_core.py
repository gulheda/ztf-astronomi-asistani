import sqlite3
import unittest
from datetime import datetime, timedelta, timezone
from astro_assistant.core import connect, insert_alerts, seed_demo, parse_query, query_alerts
from astro_assistant.dataset import group_split


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 17, 12, tzinfo=timezone.utc)
        self.db = connect()
        seed_demo(self.db, self.now)

    def tearDown(self):
        self.db.close()

    def run_query(self, text, **kwargs):
        return query_alerts(self.db, parse_query(text), self.now, **kwargs)

    def test_turkish_and_time_window(self):
        q = parse_query("SON 3 GÜNDEKİ SÜPERNOVALAR")
        self.assertEqual((q.hours, q.kind), (72, "supernova"))
        rows = self.run_query("Son 24 saatteki olaylar", demo=True)
        self.assertTrue(rows)
        self.assertTrue(all(self.now-timedelta(hours=24) <= datetime.fromisoformat(r["observed_at"]) <= self.now for r in rows))

    def test_brightest_same_band(self):
        rows = self.run_query("Son 3 gündeki g bandında en parlak ilk 4 olay", demo=True)
        self.assertEqual(len(rows), 4)
        self.assertEqual([r["magnitude"] for r in rows], sorted(r["magnitude"] for r in rows))
        self.assertTrue(all(r["band"] == "g" for r in rows))
        with self.assertRaises(ValueError):
            self.run_query("en parlak olaylar", demo=True)

    def test_unsupported_conditions_and_injection(self):
        for text in ("", "Mars hava durumu", "olaylar; DROP TABLE alerts", "olaylar parlaklık 18 altında",
                     "son 0 saatteki olaylar", "ilk 201 olay", "süpernova olmayan olaylar"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_query(text)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM alerts").fetchone()[0], 36)

    def test_demo_excluded_by_default(self):
        self.assertEqual(self.run_query("olaylar"), [])

    def test_threshold_and_type(self):
        rows = self.run_query("son 3 gündeki süpernovalar", demo=True, threshold=0.8)
        self.assertTrue(rows)
        self.assertTrue(all(r["kind"] == "supernova" and r["real_score"] >= 0.8 and r["kind_source"] for r in rows))

    def test_future_excluded(self):
        row = dict(self.db.execute("SELECT * FROM alerts LIMIT 1").fetchone())
        row.update(alert_id="future", observed_at=self.now+timedelta(hours=1), real_score=1)
        insert_alerts(self.db, [row])
        self.assertNotIn("future", [r["alert_id"] for r in self.run_query("olaylar", demo=True)])

    def test_invalid_record_is_not_inserted(self):
        row = dict(self.db.execute("SELECT * FROM alerts LIMIT 1").fetchone())
        row.update(alert_id="invalid", ra=400)
        with self.assertRaises(sqlite3.IntegrityError):
            insert_alerts(self.db, [row])
        row.update(ra=20, kind="supernova", kind_source=None)
        with self.assertRaises(ValueError):
            insert_alerts(self.db, [row])

    def test_group_split_no_object_leakage(self):
        ids = ["obj-%02d" % i for i in range(30) for _ in range(3)]
        split = group_split(ids)
        groups = {k: {ids[i] for i in v} for k, v in split.items()}
        self.assertFalse(groups["train"] & groups["test"])
        self.assertFalse(groups["train"] & groups["validation"])
        self.assertFalse(groups["validation"] & groups["test"])
        self.assertEqual(sum(map(len, split.values())), len(ids))
        self.assertEqual(split, group_split(ids))


if __name__ == "__main__":
    unittest.main()
