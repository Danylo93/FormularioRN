from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ..data.types import Bar, Order, Position, Signal


@dataclass
class PaperBroker:
    settings: object
    equity: float = field(default_factory=lambda: 10000.0)
    positions: List[Position] = field(default_factory=list)
    orders: List[Order] = field(default_factory=list)

    def place_order(self, signal: Signal) -> Order:
        order = Order(id=f"ord-{len(self.orders)+1}", signal=signal, filled=True, fill_time=datetime.utcnow())
        self.orders.append(order)
        pos = Position(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            side=signal.side,
            entry=signal.entry,
            size=signal.size,
            stop=signal.stop,
            tp1=signal.tp1,
            tp2=signal.tp2,
            open_time=order.fill_time,
        )
        self.positions.append(pos)
        return order

    def on_bar(self, bar: Bar) -> None:
        for pos in list(self.positions):
            if not pos.is_open:
                continue
            # Checagem de TP/SL
            if pos.side == "long":
                if bar.low <= pos.stop:
                    pnl = (pos.stop - pos.entry) * pos.size
                    pos.realized_pnl += pnl
                    pos.is_open = False
                    pos.close_time = bar.end_time
                    self.equity += pnl
                    continue
                if not pos.tp1_hit and bar.high >= pos.tp1:
                    # Realiza metade
                    pnl = (pos.tp1 - pos.entry) * (pos.size * 0.5)
                    pos.realized_pnl += pnl
                    pos.size *= 0.5
                    pos.tp1_hit = True
                    self.equity += pnl
                if bar.high >= pos.tp2:
                    pnl = (pos.tp2 - pos.entry) * pos.size
                    pos.realized_pnl += pnl
                    pos.is_open = False
                    pos.close_time = bar.end_time
                    self.equity += pnl
            else:  # short
                if bar.high >= pos.stop:
                    pnl = (pos.entry - pos.stop) * pos.size
                    pos.realized_pnl += pnl
                    pos.is_open = False
                    pos.close_time = bar.end_time
                    self.equity += pnl
                    continue
                if not pos.tp1_hit and bar.low <= pos.tp1:
                    pnl = (pos.entry - pos.tp1) * (pos.size * 0.5)
                    pos.realized_pnl += pnl
                    pos.size *= 0.5
                    pos.tp1_hit = True
                    self.equity += pnl
                if bar.low <= pos.tp2:
                    pnl = (pos.entry - pos.tp2) * pos.size
                    pos.realized_pnl += pnl
                    pos.is_open = False
                    pos.close_time = bar.end_time
                    self.equity += pnl

