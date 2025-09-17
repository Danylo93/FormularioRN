from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from config import Settings
from ..data.yahoo import download_bars
from ..signals.engine import build_default_engine
from ..broker.paper import PaperBroker


def run_backtest(settings: Settings, start: str, end: str) -> None:
    bars = download_bars(settings.symbol, settings.timeframe, start=start, end=end)
    engine = build_default_engine(settings)
    broker = PaperBroker(settings)

    for bar in bars:
        signal = engine.on_bar(bar)
        if signal is not None:
            broker.place_order(signal)
        broker.on_bar(bar)

    # Relatório simples
    total = broker.equity
    print({
        "symbol": settings.symbol,
        "timeframe": settings.timeframe,
        "final_equity": round(total, 2),
        "num_trades": len(broker.orders),
        "open_positions": sum(1 for p in broker.positions if p.is_open),
    })

