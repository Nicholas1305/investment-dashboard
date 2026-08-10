"""ECB Data Portal (SDW) wrapper. Free, keyless SDMX 2.1 REST API.

Docs: https://data.ecb.europa.eu/help/api/data-examples
"""
import csv
import io

import requests

BASE_URL = "https://data-api.ecb.europa.eu/service/data"

# Daily fixed-rate main refinancing operations level, euro area.
MRR_FLOW = "FM"
MRR_KEY = "D.U2.EUR.4F.KR.MRR_FR.LEV"

# Monthly HICP, all-items, euro area, annual rate of change.
HICP_FLOW = "ICP"
HICP_KEY = "M.U2.N.000000.4.ANR"


def _fetch_csv(flow: str, key: str, last_n: int = 500) -> list[dict]:
    url = f"{BASE_URL}/{flow}/{key}"
    resp = requests.get(
        url,
        params={"format": "csvdata", "lastNObservations": last_n},
        headers={"Accept": "text/csv"},
        timeout=20,
    )
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    rows = [r for r in reader if r.get("OBS_VALUE") not in (None, "")]
    # ECB returns observations in ascending TIME_PERIOD order.
    return rows


def main_refinancing_rate() -> dict:
    raw_rows = _fetch_csv(MRR_FLOW, MRR_KEY)
    if not raw_rows:
        raise ValueError("No ECB MRR observations returned")
    # Compare as floats, never as raw strings - a source can format the same
    # value inconsistently across observations (seen on FRED; guard here too).
    rows = [{"period": r["TIME_PERIOD"], "value": float(r["OBS_VALUE"])} for r in raw_rows]
    rows.sort(key=lambda r: r["period"])
    latest = rows[-1]
    current_value = latest["value"]
    since = latest["period"]
    for r in reversed(rows):
        if r["value"] != current_value:
            break
        since = r["period"]
    result = {"current": {"value": round(current_value, 2), "since": since}}

    prev_rows = [r for r in rows if r["value"] != current_value]
    if prev_rows:
        prev_value = prev_rows[-1]["value"]
        prev_since = prev_rows[-1]["period"]
        for r in reversed(prev_rows):
            if r["value"] != prev_value:
                break
            prev_since = r["period"]
        result["previous"] = {"value": round(prev_value, 2), "since": prev_since}
    return result


def hicp_eu_yoy() -> dict:
    rows = _fetch_csv(HICP_FLOW, HICP_KEY, last_n=3)
    if not rows:
        raise ValueError("No ECB HICP observations returned")
    rows.sort(key=lambda r: r["TIME_PERIOD"])
    latest = rows[-1]
    return {"value": round(float(latest["OBS_VALUE"]), 1), "date": latest["TIME_PERIOD"]}


def fetch_all() -> dict:
    data = {"ecb_main_rate": main_refinancing_rate()}
    try:
        data["hicp_eu_yoy"] = hicp_eu_yoy()
    except Exception as exc:  # HICP is optional/secondary within this module
        data["hicp_eu_yoy_error"] = str(exc)
    return data
