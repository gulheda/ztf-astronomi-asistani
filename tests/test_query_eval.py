import unittest

from tests import query_eval


class QueryEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = query_eval.run()

    def test_set_is_large_enough(self):
        self.assertGreaterEqual(self.summary["total"], 50)
        self.assertGreater(self.summary["empty_result_cases"], 0)

    def test_supported_queries_meet_plan_targets(self):
        # DENEY_PLANI.md: desteklenen sorgularda en az %90 tam eslesme.
        self.assertGreaterEqual(self.summary["condition_accuracy"], 0.9)
        self.assertGreaterEqual(self.summary["exact_result_match"], 0.9)

    def test_unsupported_queries_are_never_silently_filtered(self):
        self.assertEqual(self.summary["correctly_rejected"], 1.0)


if __name__ == "__main__":
    unittest.main()
