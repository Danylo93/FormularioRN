from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

import pandas as pd
import yfinance as yf

from .types import Bar


TF_TO_YF = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "60m",
    "4h": "240m",
    "1d": "1d",
}


def download_bars(symbol: str, timeframe: str, start: str | None = None, end: str | None = None, limit: int | None = None) -> List[Bar]:
    interval = TF_TO_YF[timeframe]
    df = yf.download(symbol, interval=interval, start=start, end=end, progress=False)
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    df = df.dropna()
    if limit is not None:
        df = df.tail(limit)

    bars: List[Bar] = []
    for idx, row in df.iterrows():
        end_time = pd.Timestamp(idx).to_pydatetime()
        bars.append(Bar(
            symbol=symbol,
            timeframe=timeframe,
            end_time=end_time,
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row.get("volume", 0.0)),
        ))
    return bars

