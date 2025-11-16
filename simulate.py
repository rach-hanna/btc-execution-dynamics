# src/simulate.py
import numpy as np
import pandas as pd

def simulate_price_paths(S0, mu_ann, sigma_ann, horizon_min, dt_min, n_paths, seed=42):
    """
    gbm monte carlo on minute grid returning array shape (n_paths, n_steps+1) and time index
    """
    rng = np.random.default_rng(seed)
    n_steps = int(horizon_min // dt_min)
    dt_years = (dt_min / 60.0) / (24.0 * 365.0)  # minutes -> years
    mu = mu_ann
    sigma = sigma_ann

    S = np.empty((n_paths, n_steps + 1), dtype=float)
    S[:, 0] = S0
    for t in range(1, n_steps + 1):
        z = rng.standard_normal(n_paths)
        S[:, t] = S[:, t-1] * np.exp((mu - 0.5 * sigma**2) * dt_years + sigma * np.sqrt(dt_years) * z)
    time_index = np.arange(n_steps + 1) * dt_min
    return S, time_index

def _size_impact_bps(qty_btc, adv_btc, k=10.0, alpha=0.6):
    """
    simple nonlinear size-based impact in basis points:
      impact_bps = sign(q) * k * (|q|/ADV)^alpha
    """
    if adv_btc <= 0:
        return 0.0
    mag = (abs(qty_btc) / adv_btc) ** alpha
    return np.sign(qty_btc) * k * mag

def simulate_execution(paths, order_qty_btc, adv_btc, k_impact=10.0, alpha=0.6, slip_noise_bps=6.0, fee_bps=2.0, seed=7):
    """
    one shot execution at horizon: take terminal mid, apply size impact + noise + fees
    returns execution prices per path, slippage in bps and P&L
    """
    rng = np.random.default_rng(seed)
    S0 = paths[:, 0]
    ST = paths[:, -1]

    # deterministic size impact (bps) + random microstructure noise (bps)
    size_bps = _size_impact_bps(order_qty_btc, adv_btc, k=k_impact, alpha=alpha)
    noise_bps = rng.normal(loc=0.0, scale=slip_noise_bps, size=len(ST))
    total_bps = size_bps + noise_bps + np.sign(order_qty_btc) * fee_bps  # add fees in direction of trade

    # convert bps to price impact on terminal mid
    exec_prices = ST * (1 + (total_bps / 10000.0))
    direction = np.sign(order_qty_btc)  # +1 buy, -1 sell

    # slippage vs starting mid 
    slippage_bps = direction * ( (exec_prices - ST) / ST ) * 10000.0

    # P&L vs reference ideal instant fill at S0 
    # if buy P&L = -(exec_price - S0) * qty ; if sell P&L = +(exec_price - S0) * |qty|
    pnl = -direction * (exec_prices - S0) * abs(order_qty_btc)

    return exec_prices, slippage_bps, pnl

def summarize_metrics(S0, qty, slippage_bps, pnl):
    """
    return small dataframe of metrics
    """
    def var_es(x, alpha=0.99):
        q = np.quantile(x, 1 - alpha)
        es = x[x <= q].mean() if (x <= q).any() else q
        return q, es

    var95, es95 = var_es(pnl, 0.95)
    var99, es99 = var_es(pnl, 0.99)
    m = {
        "metric": [
            "start mid (USDT)", "order qty (BTC)", "avg slippage (bps)",
            "P (loss)", "μ(P&L) (USDT)", "σ(P&L)", "VaR₉₅", "ES₉₅", "VaR₉₉", "ES₉₉"
        ],
        "value": [
            f"{S0:,.2f}", f"{qty}",
            f"{np.mean(slippage_bps):.2f}",
            f"{(pnl < 0).mean():.1%}",
            f"{pnl.mean():,.2f}",
            f"{pnl.std(ddof=1):,.2f}",
            f"{var95:,.2f}", f"{es95:,.2f}",
            f"{var99:,.2f}", f"{es99:,.2f}",
        ],
    }
    return pd.DataFrame(m)