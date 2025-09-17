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


def screen_pairs(
    timeframe: str = "15m",
    lookback_bars: int = 800,
    news_filter: NewsFilter | None = None,
    rr_min: float = 1.2,
    align_m5_m15: bool = True,
    top_n: int = 20,
) -> List[Opportunity]:
    opps: List[Opportunity] = []
    for symbol in PAIRS:
        bars_anchor = download_bars(symbol, timeframe, start=None, end=None, limit=lookback_bars)
        if len(bars_anchor) < 210:
            continue

        # Alinhamento M5/M15 opcional
        trend_anchor = None
        trend_other = None
        if align_m5_m15:
            other_tf = "5m" if timeframe == "15m" else "15m"
            bars_other = download_bars(symbol, other_tf, start=None, end=None, limit=lookback_bars)
            if len(bars_other) < 210:
                continue
            piv_anchor = detect_pivots(bars_anchor, lookback=3)
            piv_other = detect_pivots(bars_other, lookback=3)
            trend_anchor = determine_dow_trend(piv_anchor)
            trend_other = determine_dow_trend(piv_other)
            if trend_anchor not in {"up", "down"} or trend_other not in {"up", "down"}:
                continue
            if trend_anchor != trend_other:
                continue
            # SMA200 nos dois timeframes
            side_tmp = "long" if trend_anchor == "up" else "short"
            if not (compute_sma200_ok(bars_anchor, side_tmp) and compute_sma200_ok(bars_other, side_tmp)):
                continue
        else:
            piv_anchor = detect_pivots(bars_anchor, lookback=3)
            trend_anchor = determine_dow_trend(piv_anchor)
            if trend_anchor not in {"up", "down"}:
                continue
            side_tmp = "long" if trend_anchor == "up" else "short"
            if not compute_sma200_ok(bars_anchor, side_tmp):
                continue

        # Stop técnico no timeframe âncora
        stop: Optional[float] = None
        for p in reversed(piv_anchor):
            if side_tmp == "long" and not p.is_high:
                stop = p.price
                break
            if side_tmp == "short" and p.is_high:
                stop = p.price
                break
        if stop is None:
            continue

        entry = bars_anchor[-1].close
        if news_filter is not None:
            if not news_filter.is_quiet(symbol, bars_anchor[-1].end_time, window_minutes=30):
                continue
        tp1, tp2 = fibonacci_targets(entry, stop, side_tmp)
        risk = abs(entry - stop)
        if risk <= 0:
            continue
        rr1 = abs(tp1 - entry) / risk
        rr2 = abs(tp2 - entry) / risk
        if rr1 < rr_min:
            continue

        score = (2.0 if timeframe == "15m" else 1.5) + rr1 + 0.5 * rr2
        opps.append(Opportunity(
            symbol=symbol, timeframe=timeframe, side=side_tmp, entry=entry, stop=stop, tp1=tp1,
            rr1=rr1, rr2=rr2, score=score, reason=f"dow_{trend_anchor}+sma200"
        ))

    opps.sort(key=lambda o: o.score, reverse=True)
    return opps[:top_n]

