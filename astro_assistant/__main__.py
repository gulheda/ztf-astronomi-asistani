import argparse
import json
from datetime import datetime, timezone
from .core import connect, seed_demo, parse_query, query_alerts, explain, utc


def main():
    parser = argparse.ArgumentParser(description="ZTF astronomi asistanı başlangıç prototipi")
    parser.add_argument("query", nargs="?", default="Son 24 saatteki g bandında en parlak olaylar")
    parser.add_argument("--demo", action="store_true", help="Açıkça işaretlenmiş sentetik veri kullan")
    parser.add_argument("--db", help="Gerçek kayıt veritabanı; demo ile birleştirilemez")
    parser.add_argument("--at", help="Arşiv sorgusu için saat dilimli ISO referans zamanı")
    args = parser.parse_args()
    if args.demo == bool(args.db):
        parser.error("--demo veya --db DOSYA seçeneklerinden birini kullanın.")
    if args.db:
        from pathlib import Path
        if not Path(args.db).is_file():
            parser.error("Veritabanı bulunamadı.")
    try:
        now = utc(args.at) if args.at else datetime.now(timezone.utc)
    except ValueError as error:
        parser.error(str(error))
    db = connect(args.db or ":memory:")
    try:
        if args.demo:
            seed_demo(db, now)
        query = parse_query(args.query)
        rows = query_alerts(db, query, now, demo=args.demo)
        print(json.dumps(dict(mode="DEMO / sentetik" if args.demo else "gerçek veri",
                              filters=explain(query, now, 0.5), results=rows), ensure_ascii=False, indent=2))
    except ValueError as error:
        parser.error(str(error))
    finally:
        db.close()


if __name__ == "__main__":
    main()
