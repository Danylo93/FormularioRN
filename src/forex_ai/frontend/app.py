from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List

import streamlit as st
import pandas as pd

from config import Settings
from ..screener.runner import screen_pairs
from ..news.source import load_news_csv
from ..news.filter import NewsFilter
from ..data.yahoo import download_bars
from ..features.indicators import sma, detect_pivots


st.set_page_config(page_title="Forex AI Dow+Fibo", layout="wide")

st.title("Screener Forex AI Dow + Fibonacci")

timeframe = st.selectbox("Timeframe", ["5m", "15m"], index=1)
lookback = st.slider("Barras de histórico", min_value=200, max_value=2000, value=600, step=50)
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
        opps = screen_pairs(timeframe="15m" if timeframe == "15m" else "5m", lookback_bars=lookback, news_filter=nf)
        df = pd.DataFrame([o.__dict__ for o in opps[:10]])
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
            st.line_chart(df.set_index("time"))
        else:
            st.info("Histórico insuficiente para SMA200.")

st.markdown("Notas: As oportunidades são ranqueadas por score (Dow + SMA200 + RR de Fibonacci).")

