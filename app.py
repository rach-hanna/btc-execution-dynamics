# app.py
import os, numpy as np, pandas as pd
from plotly.io import to_html
import plotly.io as pio
from src.simulate import simulate_price_paths, simulate_execution, summarize_metrics
from src.plotting import header_card, price_fan_chart, slippage_histogram, pnl_histogram, metrics_table

# dark mode aesthetic
pio.templates.default = "plotly_dark"
try:
    pio.templates["plotly_dark"]["layout"]["font"] = {"family": "Aptos, Inter, system-ui, sans-serif", "size": 13}
except Exception:
    pass

def build_report(figs, title="BTC execution dynamics model"):
    parts = [to_html(f, include_plotlyjs=False, full_html=False, config={"displaylogo": False}) for f in figs]
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
body{{margin:0;padding:24px;background:#0f1116;color:#e6e6e6;font-family:'Aptos',sans-serif}}
.container{{max-width:1100px;margin:0 auto}}
.card{{background:#151823;border:1px solid #232637;border-radius:14px;padding:18px;box-shadow:0 6px 18px rgba(0,0,0,.35);margin-bottom:18px}}
h1{{margin:0 0 8px 0}} .sub{{opacity:.7}}
</style>
</head>
<body>
  <div class="container">
    <div class="card"><h1>BTC execution dynamics model</h1><div class="sub">monte carlo of price and execution slippage</div></div>
    <div class="card">{''.join(parts)}</div>
  </div>
  <div style="margin-top:20px;opacity:.6;font-size:12px;text-align:center;">data from binance public rest api</div>

</body>
</html>"""
    return html

if __name__ == "__main__":
    # params
    S0 = 60000.0          # starting mid price (USDT)
    horizon_min = 120     # simulate 2 hours
    dt_min = 1            # 1 minute steps
    n_paths = 5000        # monte carlo paths
    mu_ann = 0.0          # annualised drift (set near 0 for short horizons)
    sigma_ann = 0.65      # annualised vol (65% ~ BTC like)
    order_qty = 0.5       # BTC to buy (>0 buy, <0 sell)
    adv_btc = 5000.0      # stylised for scaling impact
    k_impact = 12.0       # impact coefficient (bps scale)
    alpha = 0.6           # concavity for size scaling
    slip_noise_bps = 8.0  # extra microstructure noise (bps, 1bp = 0.01%)
    fee_bps = 2.5         # explicit fee in bps

    # simulate
    paths, t = simulate_price_paths(S0, mu_ann, sigma_ann, horizon_min, dt_min, n_paths, seed=42)
    exec_prices, slippage_bps, pnl = simulate_execution(paths, order_qty, adv_btc, k_impact, alpha, slip_noise_bps, fee_bps)

    # metrics
    m = summarize_metrics(S0, order_qty, slippage_bps, pnl)
    figs = [
        header_card(S0=S0, qty=order_qty, n_paths=n_paths, horizon_min=horizon_min),
        price_fan_chart(paths, t, title="price fan (median and percentile bands)"),
        slippage_histogram(slippage_bps, title="execution slippage distribution (bps)"),
        pnl_histogram(pnl, title="realised execution p&l distribution (USDT)"),
        metrics_table(m, title="summary metrics")
    ]

    # output
    os.makedirs("output", exist_ok=True)
    html = build_report(figs)
    with open("output/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("saved to output/index.html")