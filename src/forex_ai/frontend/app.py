from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List

import streamlit as st
import pandas as pd
import plotly.express as px

from config import Settings
from ..screener.runner import screen_pairs
from ..news.source import load_news_csv
from ..news.filter import NewsFilter
from ..data.yahoo import download_bars
from ..features.indicators import sma, detect_pivots


st.set_page_config(page_title="Forex AI Dow+Fibo", layout="wide")

st.title("Screener Forex AI Dow + Fibonacci")

timeframe = st.selectbox("Timeframe", ["5m", "15m"], index=1)
lookback = st.slider("Barras de histórico", min_value=200, max_value=2000, value=800, step=50)
rr_min = st.slider("RR mínimo (TP1/Risco)", min_value=0.5, max_value=3.0, value=1.2, step=0.1)
align = st.checkbox("Alinhar M5 e M15", value=True)
news_csv = st.text_input("CSV de notícias (opcional)")

col1, col2 = st.columns([1, 3])
with col1:
    st.subheader("Oportunidades (Top 10)")
    if st.button("Executar Busca"):
        nf = None
        if news_csv:
            try:
                events = load_news_csv(news_csv)
                nf = NewsFilter(events)
            except Exception as e:
                st.warning(f"Falha ao carregar CSV de notícias: {e}")
        opps = screen_pairs(
            timeframe="15m" if timeframe == "15m" else "5m",
            lookback_bars=lookback,
            news_filter=nf,
            rr_min=rr_min,
            align_m5_m15=align,
            top_n=20,
        )
        df = pd.DataFrame([o.__dict__ for o in opps])
        st.session_state["opps_df"] = df
    if "opps_df" in st.session_state:
        st.dataframe(st.session_state["opps_df"])

with col2:
    st.subheader("Gráfico e SMA200 (par selecionado)")
    symbol = st.text_input("Par (Yahoo)", value="EURUSD=X")
    if st.button("Carregar Gráfico"):
        bars = download_bars(symbol, timeframe="15m" if timeframe == "15m" else "5m", limit=lookback)
        if len(bars) >= 200:
            closes = [b.close for b in bars]
            times = [b.end_time for b in bars]
            ma200 = [None] * len(closes)
            for i in range(len(closes)):
                if i >= 199:
                    ma200[i] = sum(closes[i-199:i+1]) / 200
            df = pd.DataFrame({
                "time": times,
                "close": closes,
                "sma200": ma200,
            })
            fig = px.line(df, x="time", y=["close", "sma200"], title=f"{symbol} - {timeframe.upper()} Close & SMA200")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Histórico insuficiente para SMA200.")

st.markdown("Notas: As oportunidades são ranqueadas por score (Dow + SMA200 + RR de Fibonacci).")

