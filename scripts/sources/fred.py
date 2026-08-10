"""FRED API wrapper (Fed Funds Target Range, US Treasuries, US CPI YoY).

Free API key required: https://fredaccount.stlouisfed.org/apikeys
Passed in via the FRED_API_KEY environment variable.
"""
import datetime as dt
import os

import requests

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def _get_observations(series_id: str, api_key: str, limit: int = 30) -> list[dict]:
    resp = requests.get(
        BASE_URL,
        params={
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit,
        },
        timeout=20,
    )
    resp.raise_for_status()
    obs = resp.json()["observations"]
    return [o for o in obs if o["value"] not in (".", None)]


def latest_value(series_id: str, api_key: str) -> dict:
    """Latest non-missing observation as {value, date}."""
    obs = _get_observations(series_id, api_key, limit=10)
    if not obs:
        raise ValueError(f"No observations for {series_id}")
    latest = obs[0]
    return {"value": float(latest["value"]), "date": latest["date"]}


def latest_and_previous_distinct(series_id: str, api_key: str) -> tuple[dict, dict | None]:
    """Latest value plus the most recent *different* value before it.

    Useful for policy rates that only change occasionally (e.g. Fed target
    range) so we can show "current since / previous since" like the sample
    report.
    """
    # FRED formats the same numeric value inconsistently across observations
    # (e.g. "3.75" vs "3.7500000000"), so compare as floats, never as raw
    # strings, or a formatting change gets mistaken for a rate change.
    obs = [{"date": o["date"], "value": float(o["value"])} for o in _get_observations(series_id, api_key, limit=200)]
    if not obs:
        raise ValueError(f"No observations for {series_id}")
    current_value = obs[0]["value"]
    since = obs[0]["date"]
    for o in obs[1:]:
        if o["value"] != current_value:
            break
        since = o["date"]
    current = {"value": current_value, "since": since}

    previous = None
    for i, o in enumerate(obs):
        if o["value"] != current_value:
            prev_value = o["value"]
            prev_since = o["date"]
            for o2 in obs[i:]:
                if o2["value"] != prev_value:
                    break
                prev_since = o2["date"]
            previous = {"value": prev_value, "since": prev_since}
            break
    return current, previous


def yoy_change(series_id: str, api_key: str) -> dict:
    """Latest value expressed as year-over-year % change (e.g. CPI)."""
    obs = _get_observations(series_id, api_key, limit=20)
    if not obs:
        raise ValueError(f"No observations for {series_id}")
    latest = obs[0]
    latest_date = dt.datetime.strptime(latest["date"], "%Y-%m-%d").date()
    target_date = latest_date.replace(year=latest_date.year - 1)
    year_ago = min(
        obs,
        key=lambda o: abs((dt.datetime.strptime(o["date"], "%Y-%m-%d").date() - target_date).days),
    )
    latest_val = float(latest["value"])
    year_ago_val = float(year_ago["value"])
    pct = (latest_val / year_ago_val - 1) * 100
    return {"value": round(pct, 1), "date": latest["date"]}


def fed_funds_target_range(api_key: str) -> dict:
    upper_cur, upper_prev = latest_and_previous_distinct("DFEDTARU", api_key)
    lower_cur, lower_prev = latest_and_previous_distinct("DFEDTARL", api_key)
    result = {
        "current": {
            "range": f"{lower_cur['value']:.2f}-{upper_cur['value']:.2f}",
            "since": upper_cur["since"],
        }
    }
    if upper_prev and lower_prev:
        result["previous"] = {
            "range": f"{lower_prev['value']:.2f}-{upper_prev['value']:.2f}",
            "since": upper_prev["since"],
        }
        result["change_bp"] = round((upper_cur["value"] - upper_prev["value"]) * 100)
    return result


def treasury_yields(api_key: str) -> dict:
    y10 = latest_value("DGS10", api_key)
    y2 = latest_value("DGS2", api_key)
    spread = round(y10["value"] - y2["value"], 2)
    return {
        "us_10y": y10,
        "us_2y": y2,
        "spread_10y_2y": {"value": spread, "date": y10["date"]},
    }


def us_cpi_yoy(api_key: str) -> dict:
    return yoy_change("CPIAUCSL", api_key)


def fetch_all() -> dict:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY environment variable is not set")
    data = {}
    data["fed_funds"] = fed_funds_target_range(api_key)
    data.update(treasury_yields(api_key))
    data["cpi_us_yoy"] = us_cpi_yoy(api_key)
    return data
