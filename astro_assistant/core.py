"""Bağımlılıksız, sınırlı Türkçe sorgu dili ve SQLite erişimi."""
import math
import re
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone


def utc(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("Zaman, saat dilimi içermelidir.")
    return value.astimezone(timezone.utc)


def iso(value):
    return utc(value).isoformat(timespec="microseconds")


@dataclass
class Query:
    hours: int = 24
    order: str = "recent"
    limit: int = 20
    kind: str = ""
    band: str = ""


def parse_query(text):
    text = text.translate(str.maketrans("İI", "iı")).lower()
    text = text.translate(str.maketrans("çğıöşü", "cgiosu")).strip()
    text = text.replace(",", " ")
    q = Query()
    recognized = False
    # Consume the entire supported grammar: never silently ignore unknown filters.
    match = re.search(r"\bson\s+(\d+)\s+(saat|gun)(?:teki|taki|te|ta|deki|daki|de|da|lik|luk|\s+icindeki|\s+icinde|\s+icerisindeki|\s+icerisinde)?\b", text)
    if match:
        recognized = True
        q.hours = int(match[1]) * (24 if match[2] == "gun" else 1)
        text = text[:match.start()] + " " + text[match.end():]
    if not 1 <= q.hours <= 24 * 365:
        raise ValueError("Zaman aralığı 1 saat ile 365 gün arasında olmalı.")
    if "en parlak" in text:
        recognized = True
        q.order = "brightest"
        text = text.replace("en parlak", " ", 1)
    elif "en yeni" in text:
        recognized = True
        text = text.replace("en yeni", " ", 1)
    match = re.search(r"\bilk\s+(\d+)\b", text)
    if match:
        recognized = True
        q.limit = int(match[1])
        text = text[:match.start()] + " " + text[match.end():]
    if not 1 <= q.limit <= 200:
        raise ValueError("Sonuç sayısı 1–200 arasında olmalı.")
    match = re.search(r"\b([gri])\s+bandinda(?:ki)?\b", text)
    if match:
        recognized = True
        q.band = match[1]
        text = text[:match.start()] + " " + text[match.end():]
    kinds = {"supernova": "supernova", "supernovalar": "supernova",
             "supernovalari": "supernova", "asteroid": "asteroid",
             "asteroidler": "asteroid", "asteroidleri": "asteroid",
             "asteroit": "asteroid", "asteroitler": "asteroid", "asteroitleri": "asteroid"}
    tokens = re.findall(r"\S+", text)
    fillers = {"olay", "olayi", "olaylar", "olaylari", "gercek", "aday", "adayi", "adaylar", "adaylari",
               "goster", "listele", "getir", "bana", "lutfen", "tane", "adet", "tum", "butun"}
    for token in tokens:
        token = token.rstrip(".?!,")
        if token in kinds and not q.kind:
            q.kind = kinds[token]
            recognized = True
        elif token in fillers:
            recognized = recognized or token not in ("lutfen", "bana", "tane", "adet", "tum", "butun")
        else:
            raise ValueError("Desteklenmeyen ifade: %s. Örnek: Son 24 saatteki en parlak olaylar" % token)
    if not recognized:
        raise ValueError("Bir olay sorgusu yazın. Örnek: Son 24 saatteki olaylar")
    return q


def connect(path=":memory:"):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS alerts (
        alert_id TEXT PRIMARY KEY, object_id TEXT NOT NULL,
        observed_at TEXT NOT NULL, ra REAL NOT NULL CHECK(ra>=0 AND ra<360),
        dec REAL NOT NULL CHECK(dec>=-90 AND dec<=90), magnitude REAL,
        band TEXT NOT NULL CHECK(band IN ('g','r','i')),
        real_score REAL NOT NULL CHECK(real_score>=0 AND real_score<=1),
        model_version TEXT NOT NULL, source TEXT NOT NULL,
        kind TEXT, kind_source TEXT,
        is_demo INTEGER NOT NULL CHECK(is_demo IN (0,1)),
        CHECK(kind IS NULL OR kind_source IS NOT NULL))""")
    db.execute("CREATE INDEX IF NOT EXISTS alert_time ON alerts(observed_at)")
    # Migrate earlier second-precision records to one comparable UTC format.
    if db.execute("PRAGMA user_version").fetchone()[0] < 1:
        with db:
            rows = db.execute("SELECT alert_id, observed_at FROM alerts").fetchall()
            db.executemany("UPDATE alerts SET observed_at=? WHERE alert_id=?",
                           [(iso(r["observed_at"]), r["alert_id"]) for r in rows])
            db.execute("PRAGMA user_version=1")
    return db


def insert_alerts(db, records):
    fields = ("alert_id", "object_id", "observed_at", "ra", "dec", "magnitude",
              "band", "real_score", "model_version", "source", "kind", "kind_source", "is_demo")
    values = []
    for record in records:
        row = dict(record)
        row["observed_at"] = iso(row["observed_at"])
        for name in ("ra", "dec", "real_score"):
            if not math.isfinite(row[name]):
                raise ValueError("Sonlu olmayan sayısal değer: " + name)
        if row.get("magnitude") is not None and not math.isfinite(row["magnitude"]):
            raise ValueError("Parlaklık sonlu olmalı veya boş bırakılmalı.")
        for name in ("alert_id", "object_id", "source", "model_version"):
            if not isinstance(row.get(name), str) or not row[name].strip():
                raise ValueError("Eksik kaynak/kimlik: " + name)
        if row.get("kind") and not row.get("kind_source"):
            raise ValueError("Olay türünün kaynağı gereklidir.")
        values.append(tuple(row.get(f) for f in fields))
    with db:
        db.executemany("INSERT INTO alerts (" + ",".join(fields) + ") VALUES (" +
                       ",".join("?" for _ in fields) + ")", values)


def query_alerts(db, query, now, threshold=0.5, demo=False):
    now = utc(now)
    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("Eşik 0–1 arasında olmalı.")
    if not 1 <= query.hours <= 8760 or not 1 <= query.limit <= 200:
        raise ValueError("Geçersiz sorgu sınırları.")
    conditions = ["observed_at >= ?", "observed_at <= ?", "real_score >= ?", "is_demo = ?"]
    args = [iso(now - timedelta(hours=query.hours)), iso(now), threshold, int(demo)]
    if query.kind:
        conditions += ["kind = ?", "kind_source IS NOT NULL"]
        args.append(query.kind)
    if query.band:
        conditions.append("band = ?")
        args.append(query.band)
    if query.order == "brightest":
        if not query.band:
            raise ValueError("Parlaklık sıralaması için g, r veya i bandını belirtin: g bandında en parlak olaylar")
        conditions.append("magnitude IS NOT NULL")
        order = "magnitude ASC, observed_at DESC, alert_id ASC"
    elif query.order == "recent":
        order = "observed_at DESC, alert_id ASC"
    else:
        raise ValueError("Desteklenmeyen sıralama.")
    sql = "SELECT * FROM alerts WHERE " + " AND ".join(conditions) + " ORDER BY " + order + " LIMIT ?"
    return [dict(r) for r in db.execute(sql, args + [query.limit])]


def seed_demo(db, now):
    """Only insert fabricated records with explicit demo provenance."""
    now = utc(now)
    records = []
    for i in range(36):
        kind = (None, "supernova", "asteroid")[i % 3]
        records.append(dict(alert_id="DEMO-%03d" % i, object_id="DEMO-OBJ-%03d" % i,
            observed_at=now - timedelta(hours=i * 2), ra=(i * 37.1) % 360,
            dec=-65 + (i * 13 % 130), magnitude=16 + (i * 7 % 45) / 10,
            band=("g", "r", "i")[i % 3], real_score=0.2 if i % 5 == 0 else 0.9,
            model_version="demo-no-model", source="synthetic-demo", kind=kind,
            kind_source="synthetic-demo" if kind else None, is_demo=1))
    insert_alerts(db, records)


def explain(query, now, threshold):
    return dict(asdict(query), reference_time_utc=iso(now), threshold=threshold,
                unit="alert", note="Aynı nesnenin birden fazla uyarısı olabilir; skor kalibre olasılık değildir.")
