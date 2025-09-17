from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal, Dict, Any


@dataclass
class Bar:
    symbol: str
    timeframe: str
    end_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


Side = Literal["long", "short"]


@dataclass
class Signal:
    symbol: str
    timeframe: str
    side: Side
    entry: float
    stop: float
    tp1: float
    tp2: float
    size: float
    reason: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "side": self.side,
            "entry": self.entry,
            "stop": self.stop,
            "tp1": self.tp1,
            "tp2": self.tp2,
            "size": self.size,
            "reason": self.reason,
        }


@dataclass
class Order:
    id: str
    signal: Signal
    filled: bool
    fill_time: datetime

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "filled": self.filled,
            "fill_time": self.fill_time.isoformat(),
            "signal": self.signal.as_dict(),
        }


@dataclass
class Position:
    symbol: str
    timeframe: str
    side: Side
    entry: float
    size: float
    stop: float
    tp1: float
    tp2: float
    realized_pnl: float = 0.0
    is_open: bool = True
    tp1_hit: bool = False
    open_time: Optional[datetime] = None
    close_time: Optional[datetime] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "side": self.side,
            "entry": self.entry,
            "size": self.size,
            "stop": self.stop,
            "tp1": self.tp1,
            "tp2": self.tp2,
            "realized_pnl": self.realized_pnl,
            "is_open": self.is_open,
            "tp1_hit": self.tp1_hit,
            "open_time": self.open_time.isoformat() if self.open_time else None,
            "close_time": self.close_time.isoformat() if self.close_time else None,
        }

