"""Yahoo Finance unofficial chart API wrapper.

Used for Gold, WTI Oil, EUR/USD spot values and for historical ETF prices
(index/sector performance table). Free, keyless. Stooq was evaluated first
but currently serves a JS bot-challenge instead of CSV from both a plain
`curl` and (very likely) GitHub Actions' shared IPs, so Yahoo's chart
endpoint is used instead. It has no official uptime guarantee either, hence
every call in fetch_data.py is wrapped so a single failure only blanks that
one field instead of the whole run.
"""
import datetime as dt

import requests

BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get_history(ticker: str, range_: str = "5y", interval: str = "1d") -> list[tuple[dt.date, float]]:
    resp = requests.get(
        BASE_URL.format(ticker=ticker),
        params={"range": range_, "interval": interval},
        headers=HEADERS,
        timeout=20,
    )
    resp.raise_for_status()
    payload = resp.json()["chart"]
    if payload.get("error"):
        raise ValueError(f"Yahoo error for {ticker}: {payload['error']}")
    result = payload["result"][0]
    timestamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    out = []
    for ts, close in zip(timestamps, closes):
        if close is None:
            continue
        out.append((dt.datetime.utcfromtimestamp(ts).date(), float(close)))
    if not out:
        raise ValueError(f"No usable close prices for {ticker}")
    return out


def _closest(history: list[tuple[dt.date, float]], target: dt.date) -> tuple[dt.date, float]:
    return min(history, key=lambda h: abs((h[0] - target).days))


def latest_spot(ticker: str) -> dict:
    history = get_history(ticker, range_="5d", interval="1d")
    date, close = history[-1]
    return {"value": round(close, 4), "date": date.isoformat()}


def performance(ticker: str) -> dict:
    """1W/1M/YTD/1Y/3Y % returns for a ticker, computed from daily closes."""
    history = get_history(ticker, range_="5y", interval="1d")
    latest_date, latest_close = history[-1]

    def pct_since(days_back: int | None = None, since_date: dt.date | None = None) -> float:
        target = since_date or (latest_date - dt.timedelta(days=days_back))
        _, ref_close = _closest(history, target)
        return round((latest_close / ref_close - 1) * 100, 2)

    year_start = dt.date(latest_date.year, 1, 1)

    return {
        "1w": pct_since(days_back=7),
        "1m": pct_since(days_back=30),
        "ytd": pct_since(since_date=year_start),
        "1y": pct_since(days_back=365),
        "3y": pct_since(days_back=365 * 3),
        "as_of": latest_date.isoformat(),
    }
