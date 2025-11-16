# src/plotting.py
import numpy as np
import plotly.graph_objects as go

DARK_BG = "#0f1116"
FG = "#e6e6e6"

def _layout(fig, title):
    fig.update_layout(
        title=title,
        margin=dict(l=36, r=36, t=48, b=36),
        height=520,
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(color=FG)
    )
    return fig

def header_card(S0, qty, n_paths, horizon_min):
    fig = go.Figure()
    txt = (
        f"<b>BTC execution visuals</b><br>"
        f"<span style='opacity:.75'>S₀: {S0:,.2f} USDT &nbsp; &nbsp; qty: {qty} BTC "
        f"&nbsp; &nbsp; paths: {n_paths:,} &nbsp; &nbsp; horizon: {horizon_min} min</span>"
    )
    fig.add_annotation(x=0, y=1, xref="paper", yref="paper", showarrow=False, align="left", text=txt)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(
        margin=dict(l=24, r=24, t=20, b=12),
        height=140,
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(color=FG)
    )
    return fig

def price_fan_chart(S, t, title=""):
    pct = [5, 25, 50, 75, 95]
    bands = {p: np.percentile(S, p, axis=0) for p in pct}

    # tight y range
    y_min = float(np.min(bands[5])) * 0.995
    y_max = float(np.max(bands[95])) * 1.005

    fig = go.Figure()
    # contrast fills
    fig.add_trace(go.Scatter(x=t, y=bands[95], line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=t, y=bands[75], fill="tonexty", name="75–95%", mode="lines",
                             line=dict(width=0.5), fillcolor="rgba(255,120,50,0.20)"))
    fig.add_trace(go.Scatter(x=t, y=bands[50], name="median", mode="lines",
                             line=dict(width=3)))  # thicker median
    fig.add_trace(go.Scatter(x=t, y=bands[25], fill="tonexty", name="25–50%", mode="lines",
                             line=dict(width=0.5), fillcolor="rgba(50,170,255,0.20)"))
    fig.add_trace(go.Scatter(x=t, y=bands[5],  fill="tonexty", name="5–25%",  mode="lines",
                             line=dict(width=0.5), fillcolor="rgba(120,80,255,0.20)"))

    fig.update_xaxes(title="minutes", gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(title="price (USDT)", range=[y_min, y_max], gridcolor="rgba(255,255,255,0.08)")
    return _layout(fig, title)

def slippage_histogram(slippage_bps, title=""):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=slippage_bps, nbinsx=60, name="slippage (bps)"))
    fig.update_layout(bargap=0.02)
    fig.update_xaxes(title="bps", gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(title="count", gridcolor="rgba(255,255,255,0.08)")
    return _layout(fig, title)

def pnl_histogram(pnl, title=""):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=pnl, nbinsx=80, name="P&L (USDT)"))
    fig.update_layout(bargap=0.02)
    fig.update_xaxes(title="USDT", gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(title="count", gridcolor="rgba(255,255,255,0.08)")
    return _layout(fig, title)

def metrics_table(df, title=""):
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Table(
        columnwidth=[0.55, 0.45],
        header=dict(
            values=list(df.columns),
            align="left",
            height=36,
            fill_color="#1b1e29",
            font=dict(color=FG, size=13),
            line_color="#2b2f3c"
        ),
        cells=dict(
            values=[df.iloc[:, 0], df.iloc[:, 1]],
            align="left",
            height=32,
            fill_color="#232637",
            font=dict(color=FG, size=12),
            line_color="#2b2f3c"
        )
    )])
    return _layout(fig, title)