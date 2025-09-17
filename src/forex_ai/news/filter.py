from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class NewsEvent:
    time: datetime
    currency: str
    impact: str  # low/medium/high
    title: str


class NewsFilter:
    def __init__(self, events: List[NewsEvent]):
        self.events = sorted(events, key=lambda e: e.time)

    def is_quiet(self, symbol: str, now: datetime, window_minutes: int = 30) -> bool:
        # Evita operar +/- window de eventos high relacionados às moedas do par
        base, quote = self._parse_pair(symbol)
        start = now - timedelta(minutes=window_minutes)
        end = now + timedelta(minutes=window_minutes)
        for e in self.events:
            if e.impact.lower() != "high":
                continue
            if e.currency in {base, quote} and start <= e.time <= end:
                return False
        return True

    @staticmethod
    def _parse_pair(symbol: str) -> tuple[str, str]:
        # Para tickers Yahoo como EURUSD=X, extrair EUR e USD
        if symbol.endswith("=X") and len(symbol) >= 8:
            sym = symbol[:-2]
            return sym[:3], sym[3:6]
        # Fallback simples
        return symbol[:3], symbol[3:6]

