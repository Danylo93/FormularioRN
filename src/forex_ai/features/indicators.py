from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional, Tuple

from ..data.types import Bar


def sma(values: List[float], period: int) -> Optional[float]:
    if len(values) < period or period <= 0:
        return None
    return sum(values[-period:]) / period


def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[float]:
    n = len(closes)
    if n < period + 1:
        return None
    trs: List[float] = []
    for i in range(n - period, n):
        h = highs[i]
        l = lows[i]
        c_prev = closes[i - 1]
        tr = max(h - l, abs(h - c_prev), abs(l - c_prev))
        trs.append(tr)
    return sum(trs) / len(trs)


@dataclass
class Pivot:
    index: int
    price: float
    is_high: bool  # True se topo, False se fundo


def detect_pivots(bars: List[Bar], lookback: int) -> List[Pivot]:
    pivots: List[Pivot] = []
    for i in range(lookback, len(bars) - lookback):
        is_high = all(bars[i].high >= bars[j].high for j in range(i - lookback, i + lookback + 1))
        is_low = all(bars[i].low <= bars[j].low for j in range(i - lookback, i + lookback + 1))
        if is_high:
            pivots.append(Pivot(index=i, price=bars[i].high, is_high=True))
        if is_low:
            pivots.append(Pivot(index=i, price=bars[i].low, is_high=False))
    pivots.sort(key=lambda p: p.index)
    return pivots


def determine_dow_trend(pivots: List[Pivot]) -> Optional[str]:
    # Retorna 'up', 'down' ou None
    if len(pivots) < 4:
        return None
    # considerar sequência de pivots alternados
    last = pivots[-4:]
    highs = [p for p in last if p.is_high]
    lows = [p for p in last if not p.is_high]
    if len(highs) >= 2 and len(lows) >= 2:
        hh = highs[-1].price > highs[-2].price
        hl = lows[-1].price > lows[-2].price
        if hh and hl:
            return "up"
        ll = lows[-1].price < lows[-2].price
        lh = highs[-1].price < highs[-2].price
        if ll and lh:
            return "down"
    return None


def fibonacci_targets(entry: float, stop: float, side: str) -> Tuple[float, float]:
    ext1 = 1.618
    ext2 = 2.618
    risk = abs(entry - stop)
    if side == "long":
        return entry + ext1 * risk, entry + ext2 * risk
    else:
        return entry - ext1 * risk, entry - ext2 * risk


def compute_sma200_ok(bars: List[Bar], side: str) -> bool:
    closes = [b.close for b in bars]
    ma = sma(closes, 200)
    if ma is None:
        return False
    price = closes[-1]
    if side == "long":
        return price > ma
    return price < ma

