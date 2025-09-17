from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import List, Dict, Optional

from config import Settings
from ..data.yahoo import download_bars
from ..features.indicators import detect_pivots, determine_dow_trend, compute_sma200_ok, fibonacci_targets
from ..news.filter import NewsFilter


PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "USDCAD=X", "AUDUSD=X", "NZDUSD=X",
    "EURJPY=X", "EURGBP=X", "EURCHF=X", "GBPJPY=X",
]


@dataclass
class Opportunity:
    symbol: str
    timeframe: str
    side: str
    entry: float
    stop: float
    tp1: float
    rr1: float
    rr2: float
    score: float
    reason: str


def screen_pairs(timeframe: str = "15m", lookback_bars: int = 600, news_filter: NewsFilter | None = None) -> List[Opportunity]:
    opps: List[Opportunity] = []
    for symbol in PAIRS:
        bars = download_bars(symbol, timeframe, start=None, end=None, limit=lookback_bars)
        if len(bars) < 210:
            continue
        pivots = detect_pivots(bars, lookback=3)
        trend = determine_dow_trend(pivots)
        if trend not in {"up", "down"}:
            continue

        side = "long" if trend == "up" else "short"
        if not compute_sma200_ok(bars, side):
            continue

        # stop no último pivot oposto
        stop: Optional[float] = None
        for p in reversed(pivots):
            if side == "long" and not p.is_high:
                stop = p.price
                break
            if side == "short" and p.is_high:
                stop = p.price
                break
        if stop is None:
            continue

        entry = bars[-1].close
        if news_filter is not None:
            if not news_filter.is_quiet(symbol, bars[-1].end_time, window_minutes=30):
                continue
        tp1, tp2 = fibonacci_targets(entry, stop, side)
        risk = abs(entry - stop)
        rr1 = abs(tp1 - entry) / risk if risk > 0 else 0.0
        rr2 = abs(tp2 - entry) / risk if risk > 0 else 0.0

        score = (2.0 if timeframe == "15m" else 1.5) + rr1 + 0.5 * rr2
        opps.append(Opportunity(
            symbol=symbol, timeframe=timeframe, side=side, entry=entry, stop=stop, tp1=tp1,
            rr1=rr1, rr2=rr2, score=score, reason=f"dow_{trend}+sma200"
        ))

    opps.sort(key=lambda o: o.score, reverse=True)
    return opps

