from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from forex_ai.data.yahoo import download_bars


PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "USDCAD=X", "AUDUSD=X", "NZDUSD=X",
    "EURJPY=X", "EURGBP=X", "EURCHF=X", "GBPJPY=X",
]


def trend_heatmap(timeframe: str = "15m", lookback_bars: int = 400):
    rows = []
    for s in PAIRS:
        bars = download_bars(s, timeframe, limit=lookback_bars)
        if len(bars) < 210:
            continue
        close = [b.close for b in bars]
        sma200 = sum(close[-200:]) / 200
        price = close[-1]
        bias = 1 if price > sma200 else -1
        rows.append({"pair": s, "bias": bias, "distance": (price - sma200) / sma200})
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("Sem dados suficientes.")
        return
    fig = px.imshow(df[["distance"]].T, labels=dict(x="pair", y="metric", color="dist"), x=df["pair"], y=["distance"], aspect="auto", color_continuous_scale="RdYlGn")
    st.plotly_chart(fig, use_container_width=True)


def correlation_matrix(timeframe: str = "15m", lookback_bars: int = 400):
    prices = {}
    for s in PAIRS:
        bars = download_bars(s, timeframe, limit=lookback_bars)
        if len(bars) < 50:
            continue
        prices[s] = [b.close for b in bars]
    if not prices:
        st.info("Sem dados para correlação.")
        return
    df = pd.DataFrame(prices)
    returns = df.pct_change().dropna()
    corr = returns.corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale="RdBu")
    st.plotly_chart(fig, use_container_width=True)

