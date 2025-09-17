from __future__ import annotations

from typing import List
import pandas as pd

from .types import Bar


def load_csv_bars(path: str, symbol: str, timeframe: str) -> List[Bar]:
    df = pd.read_csv(path)
    # Espera colunas: time, open, high, low, close, volume
    required = {"time", "open", "high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas faltando no CSV: {missing}")
    if "volume" not in df.columns:
        df["volume"] = 0.0
    df = df.dropna()
    bars: List[Bar] = []
    for _, row in df.iterrows():
        bars.append(Bar(
            symbol=symbol,
            timeframe=timeframe,
            end_time=pd.to_datetime(row["time"]).to_pydatetime(),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row.get("volume", 0.0)),
        ))
    return bars

