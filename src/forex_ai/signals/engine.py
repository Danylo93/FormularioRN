from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional

from config import Settings
from ..data.types import Bar, Signal
from ..features.indicators import detect_pivots, determine_dow_trend, fibonacci_targets
from ..model.online import OnlineModel


@dataclass
class SignalsEngine:
    settings: Settings
    window: Deque[Bar]
    model: OnlineModel

    def on_bar(self, bar: Bar) -> Optional[Signal]:
        self.window.append(bar)
        if len(self.window) < 60:
            return None

        bars: List[Bar] = list(self.window)
        pivots = detect_pivots(bars, self.settings.pivot_lookback)
        trend = determine_dow_trend(pivots)

        # Preparar label atrasada para treino
        label = None
        if len(bars) > self.model.horizon + 1:
            ret_future = (bars[-1].close - bars[-1 - self.model.horizon].close) / bars[-1 - self.model.horizon].close
            label = 1 if ret_future > 0 else 0
        self.model.update_with_window(bars[:-self.model.horizon] if len(bars) > self.model.horizon else bars, label)

        proba_up = self.model.predict_proba(bars)

        # Seleção de direção por Dow + IA
        side: Optional[str] = None
        reason = []
        if trend == "up" and (proba_up is None or proba_up >= self.settings.prob_threshold):
            side = "long"
            reason.append("dow_up")
        elif trend == "down" and (proba_up is None or (1 - proba_up) >= self.settings.prob_threshold):
            side = "short"
            reason.append("dow_down")

        if side is None:
            return None

        # Stop técnico: último pivot oposto
        stop: Optional[float] = None
        for p in reversed(pivots):
            if side == "long" and not p.is_high:
                stop = p.price
                break
            if side == "short" and p.is_high:
                stop = p.price
                break
        if stop is None:
            return None

        entry = bar.close
        tp1, tp2 = fibonacci_targets(entry, stop, side)

        # sizing simples baseado em risco por trade
        risk_per_trade = self.settings.risk_per_trade * self.settings.initial_equity
        risk_per_unit = abs(entry - stop)
        if risk_per_unit <= 0:
            return None
        size = max(0.0, risk_per_trade / risk_per_unit)

        return Signal(
            symbol=bar.symbol,
            timeframe=bar.timeframe,
            side=side, entry=entry, stop=stop, tp1=tp1, tp2=tp2, size=size,
            reason=",".join(reason)
        )


def build_default_engine(settings: Settings) -> SignalsEngine:
    model = OnlineModel(horizon=settings.lookahead_bars, prob_threshold=settings.prob_threshold)
    return SignalsEngine(settings=settings, window=deque(maxlen=2000), model=model)

