"""Run reproducible SQL security investigations against an in-memory lab database."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent
DEFAULTS = dict(window_seconds=300, min_users=4, min_failures=5,
                followup_seconds=600, min_bytes=10000000, user_id="alex")


def timestamp(value):
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None or stamp.microsecond:
        raise ValueError("timestamps must include timezone and use whole seconds")
    return int(stamp.astimezone(timezone.utc).timestamp())


def connect():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript((ROOT / "schema.sql").read_text(encoding="utf-8"))
    return db


def load_fixture(db):
    data = json.loads((ROOT / "data/scenario.json").read_text(encoding="utf-8"))
    with db:
        db.executemany("INSERT INTO users VALUES (?, ?, ?)", data["users"])
        db.executemany("INSERT INTO auth_events VALUES (?, ?, ?, ?, ?)",
                       [(i, timestamp(t), u, ip, outcome) for i, t, u, ip, outcome in data["auth_events"]])
        db.executemany("INSERT INTO access_events VALUES (?, ?, ?, ?, ?, ?)",
                       [(i, timestamp(t), u, ip, r, size) for i, t, u, ip, r, size in data["access_events"]])


def run_query(db, name, parameters=None):
    allowed = {p.stem: p for p in (ROOT / "queries").glob("*.sql")}
    if name not in allowed:
        raise ValueError("unknown query")
    options = DEFAULTS | (parameters or {})
    for key in ("window_seconds", "min_users", "min_failures", "followup_seconds", "min_bytes"):
        if type(options[key]) is not int or options[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    if not isinstance(options["user_id"], str) or not options["user_id"].strip():
        raise ValueError("user_id must be a nonempty string")
    return [dict(row) for row in db.execute(allowed[name].read_text(encoding="utf-8"), options)]


def report(db, parameters=None):
    return {p.stem: run_query(db, p.stem, parameters)
            for p in sorted((ROOT / "queries").glob("*.sql"))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="alex", help="account for the timeline query")
    parser.add_argument("--min-bytes", type=int, default=DEFAULTS["min_bytes"])
    args = parser.parse_args(argv)
    db = connect()
    try:
        load_fixture(db)
        result = report(db, dict(user_id=args.user, min_bytes=args.min_bytes))
        print(json.dumps(result, indent=2, sort_keys=True))
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
