from __future__ import annotations

from datetime import datetime
from typing import List

import pandas as pd

from .filter import NewsEvent


def load_news_csv(path: str) -> List[NewsEvent]:
    df = pd.read_csv(path)
    required = {"time", "currency", "impact", "title"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas faltando no CSV de notícias: {missing}")
    events: List[NewsEvent] = []
    for _, row in df.iterrows():
        events.append(NewsEvent(
            time=pd.to_datetime(row["time"]).to_pydatetime(),
            currency=str(row["currency"]).upper(),
            impact=str(row["impact"]).lower(),
            title=str(row["title"]),
        ))
    return events

