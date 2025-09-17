from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

from config import Settings
from ..screener.runner import screen_pairs
from ..news.source import load_news_csv
from ..news.filter import NewsFilter
from ..data.yahoo import download_bars
from ..features.indicators import sma, detect_pivots
from .dashboards import trend_heatmap, correlation_matrix


st.set_page_config(page_title="Forex AI Dow+Fibo", layout="wide")

st.title("Screener Forex AI Dow + Fibonacci")

api_url = st.text_input("API URL", value="http://localhost:8000")
col_auth = st.columns(3)
with col_auth[0]:
	user_id = st.text_input("User ID", value="demo")
with col_auth[1]:
	user_type = st.selectbox("User Type", options=[1, 2], index=0)
with col_auth[2]:
	if st.button("Login/API Token"):
		try:
			resp = requests.post(f"{api_url}/auth/token", timeout=15, params={"user_id": user_id, "user_type": user_type})
			resp.raise_for_status()
			st.session_state["token"] = resp.json().get("access_token")
			st.success("Token obtido")
		except Exception as e:
			st.error(f"Falha ao obter token: {e}")

headers = {}
if "token" in st.session_state:
	headers["Authorization"] = f"Bearer {st.session_state['token']}"

# Tabs
main_tab, trends_tab, corr_tab, news_tab = st.tabs(["Screener", "Tendência (Heatmap)", "Correlação", "Notícias (TE)"])

with main_tab:
	timeframe = st.selectbox("Timeframe", ["5m", "15m"], index=1)
	lookback = st.slider("Barras de histórico", min_value=200, max_value=2000, value=800, step=50)
	rr_min = st.slider("RR mínimo (TP1/Risco)", min_value=0.5, max_value=3.0, value=1.2, step=0.1)
	align = st.checkbox("Alinhar M5 e M15", value=True)
	news_csv = st.text_input("CSV de notícias (opcional)")

	col1, col2 = st.columns([1, 3])
	with col1:
		st.subheader("Oportunidades (Top)")
		use_api = st.checkbox("Usar API protegida", value=False)
		if st.button("Executar Busca"):
			nf = None
			if news_csv:
				try:
					events = load_news_csv(news_csv)
					nf = NewsFilter(events)
				except Exception as e:
					st.warning(f"Falha ao carregar CSV de notícias: {e}")
			if use_api:
				if not headers.get("Authorization"):
					st.error("Faça login para usar a API")
				else:
					try:
						params = {
							"timeframe": "15m" if timeframe == "15m" else "5m",
							"rr_min": rr_min,
							"align": align,
							"top_n": 20,
							"avoid_news": True,
						}
						resp = requests.get(f"{api_url}/screener", headers=headers, params=params, timeout=30)
						resp.raise_for_status()
						data = resp.json()
						st.session_state["opps_df"] = pd.DataFrame(data)
					except Exception as e:
						st.error(f"Erro no screener API: {e}")
			else:
				opps = screen_pairs(
					timeframe="15m" if timeframe == "15m" else "5m",
					lookback_bars=lookback,
					news_filter=nf,
					rr_min=rr_min,
					align_m5_m15=align,
					top_n=20,
				)
				st.session_state["opps_df"] = pd.DataFrame([o.__dict__ for o in opps])
		if "opps_df" in st.session_state and not st.session_state["opps_df"].empty:
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

with trends_tab:
	st.subheader("Heatmap de Tendência vs SMA200")
	tf = st.selectbox("Timeframe (heatmap)", ["5m", "15m"], index=1, key="tf_heat")
	trend_heatmap(tf)

with corr_tab:
	st.subheader("Matriz de Correlação de Retornos")
	tf2 = st.selectbox("Timeframe (correlação)", ["5m", "15m"], index=1, key="tf_corr")
	correlation_matrix(tf2)

st.markdown("Notas: Faça login para usar a API segura. O screener local não requer token.")

with news_tab:
	st.subheader("TradingEconomics - Carregar eventos (alta importância)")
	te_key = st.text_input("TE API Key (user:pass ou chave)")
	countries = st.text_input("Países (CSV)", value="USA,EUR,GBR,JPN,CAN,AUS,NZL,CHN")
	if st.button("Atualizar notícias no servidor"):
		if not headers.get("Authorization"):
			st.error("Faça login para usar a API")
		else:
			try:
				resp = requests.post(f"{api_url}/news/refresh", headers=headers, params={"te_api_key": te_key, "countries": countries, "impact": "high"}, timeout=45)
				resp.raise_for_status()
				st.success(f"Eventos carregados: {resp.json().get('loaded')}")
			except Exception as e:
				st.error(f"Erro ao atualizar notícias: {e}")

