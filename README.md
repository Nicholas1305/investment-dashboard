# Investment Dashboard

Persönliches Markt-Dashboard: Fear &amp; Greed Index, Leitzinsen (EZB/Fed),
US-Renditen &amp; Inflation, Rohstoffe/Währungen sowie Index- und
Sektor-Performance – auf einen Blick, wöchentlich automatisch aktualisiert.

## Aufbau

- `scripts/fetch_data.py` + `scripts/sources/*.py` – ziehen die Daten von
  CNN (Fear &amp; Greed), ECB (Leitzins/HICP), FRED (Fed-Zinsen,
  US-Renditen, US-CPI) und Yahoo Finance (Gold, Öl, EUR/USD,
  ETF-Performance) und schreiben `data/latest.json` sowie einen
  Tages-Snapshot unter `data/history/`.
- `index.html`, `style.css`, `app.js` – statisches Dashboard, liest
  `data/latest.json` und `data/history/*.json` (für die Trendcharts).
- `.github/workflows/update-data.yml` – führt das Fetch-Skript wöchentlich
  (Montag 06:00 UTC) automatisch aus und committed die aktualisierten Daten.

Fällt eine einzelne Datenquelle aus, bricht der Lauf nicht ab – das
betroffene Feld wird `null` und im Dashboard als "n. v." markiert; alle
anderen Werte werden trotzdem aktualisiert.

## Lokal einrichten

```bash
pip install -r scripts/requirements.txt
```

Kostenlosen FRED-API-Key holen: https://fredaccount.stlouisfed.org/apikeys
(nur für Fed-Zinsen, US-Renditen, US-CPI nötig).

```bash
# Windows PowerShell
$env:FRED_API_KEY = "dein-key"
python scripts/fetch_data.py
```

Danach `index.html` über einen lokalen Server öffnen (nicht direkt per
`file://`, da `fetch()` sonst durch CORS blockiert wird), z. B.:

```bash
python -m http.server 8000
```

## Neue Kennzahl hinzufügen

1. Ticker/Serie in `scripts/config.py` ergänzen (bei ETFs) oder neue
   Quelle unter `scripts/sources/` anlegen.
2. Feld in `scripts/fetch_data.py` in den `data`-Dict aufnehmen.
3. Kachel/Zeile in `index.html` + Rendering in `app.js` ergänzen.

## GitHub-Anbindung (einmalig)

1. GitHub-Account erstellen (falls noch nicht vorhanden).
2. Neues **öffentliches** Repository anlegen (kostenlose GitHub Pages
   brauchen ein öffentliches Repo).
3. In diesem Ordner:
   ```bash
   git init
   git add .
   git commit -m "Initial dashboard"
   git branch -M main
   git remote add origin https://github.com/<user>/<repo>.git
   git push -u origin main
   ```
4. Unter *Settings → Pages*: Source auf Branch `main` setzen.
5. Unter *Settings → Secrets and variables → Actions*: neues Secret
   `FRED_API_KEY` mit dem eigenen FRED-Key anlegen.
6. Unter *Actions* den Workflow einmal manuell ausführen
   ("Run workflow"), um den ersten automatischen Lauf zu testen.
