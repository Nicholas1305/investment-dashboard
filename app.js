const NA = '<span class="value na">n. v.</span>';

function fmtNum(value, digits = 2, suffix = "") {
  if (value === null || value === undefined || Number.isNaN(value)) return null;
  return value.toLocaleString("de-DE", { minimumFractionDigits: digits, maximumFractionDigits: digits }) + suffix;
}

function fmtPct(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return null;
  const sign = value > 0 ? "+" : "";
  return sign + value.toLocaleString("de-DE", { minimumFractionDigits: digits, maximumFractionDigits: digits }) + "%";
}

function deltaClass(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "flat";
  if (value > 0) return "good";
  if (value < 0) return "bad";
  return "flat";
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (!el) return;
  if (text === null || text === undefined) {
    el.innerHTML = NA;
  } else {
    el.textContent = text;
  }
}

function pctSpan(value, digits = 2) {
  const formatted = fmtPct(value, digits);
  if (formatted === null) return '<span class="delta flat">n. v.</span>';
  return `<span class="delta ${deltaClass(value)}">${formatted}</span>`;
}

function ratingColor(rating) {
  if (!rating) return "var(--text-muted)";
  const r = rating.toLowerCase();
  if (r.includes("extreme fear")) return "var(--status-critical)";
  if (r.includes("fear")) return "var(--status-serious)";
  if (r.includes("extreme greed")) return "var(--status-good)";
  if (r.includes("greed")) return "#6dbf6d";
  return "var(--text-muted)";
}

function renderFearGreed(fg) {
  if (!fg) {
    setText("fg-value", null);
    document.getElementById("fg-rating").style.display = "none";
    return;
  }
  const current = fg.current;
  setText("fg-value", fmtNum(current.value, 1));
  const ratingEl = document.getElementById("fg-rating");
  ratingEl.textContent = current.rating;
  ratingEl.style.background = ratingColor(current.rating);
  document.getElementById("fg-marker").style.left = `${Math.max(0, Math.min(100, current.value))}%`;

  setText("fg-prev-week", fmtNum(fg.previous_week?.value, 1));
  document.getElementById("fg-prev-week-delta").innerHTML = fg.previous_week
    ? `Veränderung ${pctArrow(fg.previous_week.change)}`
    : "";
  setText("fg-prev-month", fmtNum(fg.previous_month?.value, 1));
  document.getElementById("fg-prev-month-delta").innerHTML = fg.previous_month
    ? `Veränderung ${pctArrow(fg.previous_month.change)}`
    : "";

  const momentum = fg.subindicators?.sp500_momentum;
  const vix = fg.subindicators?.vix_volatility;
  setText("fg-momentum", momentum ? fmtNum(momentum.value, 1) : null);
  document.getElementById("fg-momentum-rating").textContent = momentum?.rating ?? "";
  setText("fg-vix", vix ? fmtNum(vix.value, 1) : null);
  document.getElementById("fg-vix-rating").textContent = vix?.rating ?? "";
}

function pctArrow(change) {
  if (change === null || change === undefined || Number.isNaN(change)) return '<span class="delta flat">n. v.</span>';
  const arrow = change > 0 ? "▲" : change < 0 ? "▼" : "→";
  const cls = deltaClass(change);
  const sign = change > 0 ? "+" : "";
  return `<span class="delta ${cls}">${arrow} ${sign}${change.toLocaleString("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}</span>`;
}

function rateRow(label, value) {
  return `<div class="row"><span class="k">${label}</span><span class="v">${value ?? "n. v."}</span></div>`;
}

function renderRates(ecb, fred) {
  const ecbRate = ecb?.ecb_main_rate;
  let ecbHtml = "";
  if (ecbRate?.current) {
    ecbHtml += `<div class="sub" style="margin-bottom:6px;">Aktuell seit ${ecbRate.current.since}</div>`;
    ecbHtml += rateRow("Hauptrefinanzierung", fmtNum(ecbRate.current.value, 2, " %"));
    if (ecbRate.previous) {
      ecbHtml += `<div class="sub" style="margin:10px 0 6px;">Vorheriger Satz seit ${ecbRate.previous.since}</div>`;
      ecbHtml += rateRow("Hauptrefinanzierung", fmtNum(ecbRate.previous.value, 2, " %"));
    }
  } else {
    ecbHtml = `<div class="sub">Daten nicht verfügbar</div>`;
  }
  document.getElementById("ecb-rows").innerHTML = ecbHtml;

  const fedRate = fred?.fed_funds;
  let fedHtml = "";
  if (fedRate?.current) {
    fedHtml += `<div class="sub" style="margin-bottom:6px;">Aktuell seit ${fedRate.current.since}</div>`;
    fedHtml += rateRow("Zinsspanne", fedRate.current.range);
    if (fedRate.change_bp !== undefined) fedHtml += rateRow("Letzte Änderung", `${fedRate.change_bp > 0 ? "+" : ""}${fedRate.change_bp} bp`);
    if (fedRate.previous) {
      fedHtml += `<div class="sub" style="margin:10px 0 6px;">Vorheriger Satz seit ${fedRate.previous.since}</div>`;
      fedHtml += rateRow("Zinsspanne", fedRate.previous.range);
    }
  } else {
    fedHtml = `<div class="sub">Daten nicht verfügbar</div>`;
  }
  document.getElementById("fed-rows").innerHTML = fedHtml;
}

function renderYieldsAndInflation(fred, ecb) {
  setText("us10y", fred?.us_10y ? fmtNum(fred.us_10y.value, 2, "%") : null);
  setText("us10y-date", fred?.us_10y ? `Stand ${fred.us_10y.date}` : "");
  setText("us2y", fred?.us_2y ? fmtNum(fred.us_2y.value, 2, "%") : null);
  setText("us2y-date", fred?.us_2y ? `Stand ${fred.us_2y.date}` : "");
  setText("spread", fred?.spread_10y_2y ? fmtNum(fred.spread_10y_2y.value, 2, " pp") : null);
  setText("spread-date", fred?.spread_10y_2y ? `Stand ${fred.spread_10y_2y.date}` : "");
  setText("cpi-us", fred?.cpi_us_yoy ? fmtNum(fred.cpi_us_yoy.value, 1, "%") : null);
  setText("cpi-us-date", fred?.cpi_us_yoy ? `Stand ${fred.cpi_us_yoy.date}` : "");
  setText("hicp-eu", ecb?.hicp_eu_yoy ? fmtNum(ecb.hicp_eu_yoy.value, 1, "%") : null);
  setText("hicp-eu-date", ecb?.hicp_eu_yoy ? `Stand ${ecb.hicp_eu_yoy.date}` : "");
}

function renderCommodities(cf) {
  setText("gold", cf?.gold_usd_oz ? "$ " + fmtNum(cf.gold_usd_oz.value, 0) : null);
  setText("gold-date", cf?.gold_usd_oz ? `Stand ${cf.gold_usd_oz.date}` : "");
  setText("wti", cf?.wti_usd_bbl ? "$ " + fmtNum(cf.wti_usd_bbl.value, 2) : null);
  setText("wti-date", cf?.wti_usd_bbl ? `Stand ${cf.wti_usd_bbl.date}` : "");
  setText("eurusd", cf?.eur_usd ? fmtNum(cf.eur_usd.value, 4) : null);
  setText("eurusd-date", cf?.eur_usd ? `Stand ${cf.eur_usd.date}` : "");
}

function renderPerfTable(bodyId, rows) {
  const tbody = document.getElementById(bodyId);
  if (!rows || !rows.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="value na">Daten nicht verfügbar</td></tr>`;
    return;
  }
  tbody.innerHTML = rows
    .map(
      (r) => `<tr>
        <td>${r.name} <span style="color:var(--text-muted);font-size:11px;">${r.ticker}</span></td>
        <td>${pctSpan(r["1w"])}</td>
        <td>${pctSpan(r["1m"])}</td>
        <td>${pctSpan(r["ytd"])}</td>
        <td>${pctSpan(r["1y"])}</td>
        <td>${pctSpan(r["3y"])}</td>
      </tr>`
    )
    .join("");
}

function renderErrors(errors) {
  const banner = document.getElementById("errors-banner");
  if (!errors || !errors.length) {
    banner.classList.remove("show");
    return;
  }
  banner.classList.add("show");
  banner.textContent = `Einige Datenquellen waren beim letzten Update nicht erreichbar (${errors.length}): betroffene Werte sind als "n. v." markiert.`;
}

function buildLineChart(container, points, { digits = 1, suffix = "" } = {}) {
  container.innerHTML = "";
  const valid = points.filter((p) => p.value !== null && p.value !== undefined);
  if (valid.length < 2) {
    container.innerHTML = '<div class="sub">Noch nicht genug Verlaufsdaten</div>';
    return;
  }
  const width = 560;
  const height = 140;
  const padL = 8;
  const padR = 56;
  const padT = 14;
  const padB = 20;
  const values = valid.map((p) => p.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const x = (i) => padL + (i / (valid.length - 1)) * (width - padL - padR);
  const y = (v) => padT + (1 - (v - min) / range) * (height - padT - padB);

  const pathD = valid.map((p, i) => `${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join(" ");
  const last = valid[valid.length - 1];
  const lastX = x(valid.length - 1);
  const lastY = y(last.value);

  const gridY1 = padT;
  const gridY2 = height - padB;

  const svg = `
    <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet">
      <line class="grid-line" x1="${padL}" y1="${gridY2}" x2="${width - padR}" y2="${gridY2}" />
      <path class="line" d="${pathD}" />
      <circle class="end-dot" cx="${lastX.toFixed(1)}" cy="${lastY.toFixed(1)}" r="4" />
      <text class="end-label" x="${(lastX + 8).toFixed(1)}" y="${(lastY + 4).toFixed(1)}">${fmtNum(last.value, digits)}${suffix}</text>
      <text class="axis-label" x="${padL}" y="${height - 4}">${valid[0].date}</text>
      <text class="axis-label" x="${width - padR}" y="${height - 4}" text-anchor="end">${last.date}</text>
    </svg>`;
  container.innerHTML = svg;
}

async function loadHistory() {
  try {
    const idx = await fetch("data/history/index.json").then((r) => (r.ok ? r.json() : []));
    const dates = idx.slice(-12); // last ~12 snapshots
    const snapshots = await Promise.all(
      dates.map((d) =>
        fetch(`data/history/${d}.json`)
          .then((r) => (r.ok ? r.json() : null))
          .catch(() => null)
      )
    );
    return dates.map((d, i) => ({ date: d, data: snapshots[i] })).filter((s) => s.data);
  } catch (e) {
    console.warn("History konnte nicht geladen werden", e);
    return [];
  }
}

async function main() {
  let data;
  try {
    data = await fetch("data/latest.json").then((r) => r.json());
  } catch (e) {
    document.getElementById("generated-at").textContent = "Daten konnten nicht geladen werden.";
    return;
  }

  document.getElementById("generated-at").textContent = `Stand: ${new Date(data.generated_at).toLocaleString("de-DE")}`;
  renderErrors(data.errors);
  renderFearGreed(data.fear_greed);
  renderRates(data.ecb, data.fred);
  renderYieldsAndInflation(data.fred, data.ecb);
  renderCommodities(data.commodities_fx);
  renderPerfTable("indices-body", data.indices);
  renderPerfTable("sectors-body", data.sectors);

  const history = await loadHistory();
  const fgPoints = history.map((s) => ({ date: s.date, value: s.data.fear_greed?.current?.value ?? null }));
  buildLineChart(document.getElementById("fg-chart"), fgPoints, { digits: 1 });

  const spreadPoints = history.map((s) => ({ date: s.date, value: s.data.fred?.spread_10y_2y?.value ?? null }));
  buildLineChart(document.getElementById("spread-chart"), spreadPoints, { digits: 2, suffix: " pp" });
}

main();
