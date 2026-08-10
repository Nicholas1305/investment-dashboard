"""Static configuration: which tickers to pull and how to label them.

Add new rows here to extend the dashboard - fetch_data.py and app.js need
no changes for additional entries in INDICES / SECTORS.
"""

GOLD_TICKER = "GC=F"
WTI_TICKER = "CL=F"
EURUSD_TICKER = "EURUSD=X"

INDICES = [
    {"name": "S&P 500", "ticker": "CSPX.L"},
    {"name": "NASDAQ-100", "ticker": "EQQQ.DE"},
    {"name": "DAX", "ticker": "EXS1.DE"},
    {"name": "STOXX Europe 600", "ticker": "EXSA.DE"},
    {"name": "EURO STOXX 50", "ticker": "EXW1.DE"},
    {"name": "MSCI World", "ticker": "IWDA.AS"},
    {"name": "MSCI Emerging Mkts", "ticker": "EIMI.L"},
    {"name": "Nikkei 225", "ticker": "EXX1.DE"},
]

SECTORS = [
    {"name": "Information Technology", "ticker": "XDWT.DE"},
    {"name": "Energy", "ticker": "SPYW.DE"},
    {"name": "Industrials", "ticker": "IS3R.DE"},
    {"name": "Health Care", "ticker": "XDWH.DE"},
    {"name": "Financials", "ticker": "XDWF.DE"},
    {"name": "Consumer Staples", "ticker": "XDWS.DE"},
    {"name": "Consumer Discretionary", "ticker": "XDWD.DE"},
    {"name": "Utilities", "ticker": "XDWU.DE"},
    {"name": "Materials", "ticker": "XDWM.DE"},
    {"name": "Communication Svcs", "ticker": "XDWC.DE"},
]
