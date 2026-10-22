"""Turkce sorgu degerlendirmesi: kosul cozumleme, sonuc kumesi eslesmesi, red ve sure.

Beklenen sonuc kimlikleri parse_query/query_alerts kullanilmadan, SQL'siz bir Python suzgeciyle
beklenen kosullardan hesaplanir. Calistir: python -m tests.query_eval
"""
import json
import statistics
import time
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path

from astro_assistant.core import Query, connect, parse_query, query_alerts, seed_demo

CASES = Path(__file__).with_name("query_eval_set.json")


def oracle(rows, expect, threshold, now):
    spec = asdict(Query(**expect))
    lower = now - timedelta(hours=spec["hours"])
    chosen = [r for r in rows
              if lower <= datetime.fromisoformat(r["observed_at"]) <= now
              and r["real_score"] >= threshold
              and (not spec["kind"] or r["kind"] == spec["kind"])
              and (not spec["band"] or r["band"] == spec["band"])]
    if spec["order"] == "brightest":
        chosen = [r for r in chosen if r["magnitude"] is not None]
        chosen.sort(key=lambda r: (r["magnitude"], -datetime.fromisoformat(r["observed_at"]).timestamp(), r["alert_id"]))
    else:
        chosen.sort(key=lambda r: (-datetime.fromisoformat(r["observed_at"]).timestamp(), r["alert_id"]))
    return [r["alert_id"] for r in chosen[:spec["limit"]]]


def run(path=CASES):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    now = datetime.fromisoformat(data["reference_time_utc"])
    db = connect()
    seed_demo(db, now)
    rows = [dict(r) for r in db.execute("SELECT * FROM alerts")]
    outcomes, timings = [], []
    for case in data["cases"]:
        started = time.perf_counter()
        outcome = dict(id=case["id"], text=case["text"], parsed=False, rejected=False, match=None)
        try:
            query = parse_query(case["text"])
            outcome["parsed"] = True
            outcome["query"] = asdict(query)
            result = query_alerts(db, query, now, case.get("threshold", 0.5), demo=True)
            outcome["result_ids"] = [r["alert_id"] for r in result]
        except ValueError as error:
            outcome["rejected"] = True
            outcome["error"] = str(error)
        timings.append((time.perf_counter() - started) * 1000)
        reject = case.get("reject")
        if reject == "parse":
            outcome["correct"] = outcome["rejected"] and not outcome["parsed"]
        elif reject == "query":
            outcome["correct"] = outcome["parsed"] and outcome["rejected"]
            outcome["conditions_ok"] = outcome["parsed"] and outcome["query"] == asdict(Query(**case["expect"]))
        else:
            outcome["conditions_ok"] = outcome["parsed"] and outcome["query"] == asdict(Query(**case["expect"]))
            expected = oracle(rows, case["expect"], case.get("threshold", 0.5), now)
            outcome["expected_ids"] = expected
            outcome["match"] = outcome.get("result_ids") == expected
            outcome["correct"] = outcome["conditions_ok"] and outcome["match"]
        outcomes.append(outcome)
    db.close()
    supported = [o for o, c in zip(outcomes, data["cases"]) if not c.get("reject")]
    unsupported = [o for o, c in zip(outcomes, data["cases"]) if c.get("reject")]
    timings.sort()
    summary = dict(
        total=len(outcomes), supported=len(supported), unsupported=len(unsupported),
        condition_accuracy=sum(o["conditions_ok"] for o in supported) / len(supported),
        exact_result_match=sum(o["match"] for o in supported) / len(supported),
        correctly_rejected=sum(o["correct"] for o in unsupported) / len(unsupported),
        empty_result_cases=sum(1 for o in supported if o["match"] and not o["expected_ids"]),
        p50_ms=statistics.median(timings), p95_ms=timings[min(len(timings) - 1, int(len(timings) * 0.95))],
        failures=[dict(id=o["id"], text=o["text"], error=o.get("error"), query=o.get("query"))
                  for o in outcomes if not o["correct"]])
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
