"""CNN Fear & Greed Index wrapper (unofficial endpoint).

No API key, but CNN blocks requests without browser-like headers (returns
HTTP 418). This is a reverse-engineered endpoint and can change/break
without notice - callers should treat failures as non-fatal.
"""
import requests

URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.cnn.com/markets/fear-and-greed",
}


def fetch_all() -> dict:
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    payload = resp.json()

    fg = payload["fear_and_greed"]
    momentum = payload["market_momentum_sp500"]
    vix = payload["market_volatility_vix"]

    def change(current: float, previous: float) -> float:
        return round(current - previous, 1)

    current_score = round(fg["score"], 1)
    return {
        "current": {"value": current_score, "rating": fg["rating"]},
        "previous_week": {
            "value": round(fg["previous_1_week"], 1),
            "change": change(current_score, fg["previous_1_week"]),
        },
        "previous_month": {
            "value": round(fg["previous_1_month"], 1),
            "change": change(current_score, fg["previous_1_month"]),
        },
        "subindicators": {
            "sp500_momentum": {"value": round(momentum["score"], 1), "rating": momentum["rating"]},
            "vix_volatility": {"value": round(vix["score"], 1), "rating": vix["rating"]},
        },
    }
