"""Pulls all dashboard metrics and writes data/latest.json (+ a dated
snapshot under data/history/) so the static frontend has something to
render.

Every data source is wrapped individually: if one fails (rate limit,
endpoint change, network issue) the run still completes and writes
whatever succeeded, with the failing fields set to null and listed under
"errors" so the frontend can show a clear "not available" state instead of
silently showing stale numbers as if they were fresh.
"""
import datetime as dt
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config
from sources import ecb, feargreed, fred, yahoo

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
HISTORY_DIR = DATA_DIR / "history"


def safe_call(errors: list[str], label: str, fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - intentionally broad, isolates one source's failure
        errors.append(f"{label}: {exc}")
        traceback.print_exc(file=sys.stderr)
        return None


def build_ticker_list(entries: list[dict], errors: list[str]) -> list[dict]:
    results = []
    for entry in entries:
        perf = safe_call(errors, f"yahoo.performance({entry['ticker']})", yahoo.performance, entry["ticker"])
        results.append({"name": entry["name"], "ticker": entry["ticker"], **(perf or {})})
    return results


def main() -> None:
    errors: list[str] = []
    now = dt.datetime.now(dt.timezone.utc)

    data = {
        "generated_at": now.isoformat(),
        "fear_greed": safe_call(errors, "feargreed", feargreed.fetch_all),
        "ecb": safe_call(errors, "ecb", ecb.fetch_all),
        "fred": safe_call(errors, "fred", fred.fetch_all),
        "commodities_fx": {
            "gold_usd_oz": safe_call(errors, "gold", yahoo.latest_spot, config.GOLD_TICKER),
            "wti_usd_bbl": safe_call(errors, "wti", yahoo.latest_spot, config.WTI_TICKER),
            "eur_usd": safe_call(errors, "eurusd", yahoo.latest_spot, config.EURUSD_TICKER),
        },
        "indices": build_ticker_list(config.INDICES, errors),
        "sectors": build_ticker_list(config.SECTORS, errors),
        "errors": errors,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    latest_path = DATA_DIR / "latest.json"
    latest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    snapshot_path = HISTORY_DIR / f"{now.date().isoformat()}.json"
    snapshot_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    index_path = HISTORY_DIR / "index.json"
    dates = sorted(p.stem for p in HISTORY_DIR.glob("*.json") if p.stem != "index")
    index_path.write_text(json.dumps(dates, indent=2), encoding="utf-8")

    if errors:
        print(f"Completed with {len(errors)} source error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
    print(f"Wrote {latest_path} and {snapshot_path}")


if __name__ == "__main__":
    main()
