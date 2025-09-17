from __future__ import annotations

import asyncio
from typing import AsyncIterator

from config import Settings
from .types import Bar
from .yahoo import download_bars


class ReplayStreamer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._bars = download_bars(
            symbol=settings.symbol,
            timeframe=settings.timeframe,
            start=None,
            end=None,
            limit=settings.history_bars,
        )

    async def stream(self, delay_seconds: float = 0.05) -> AsyncIterator[Bar]:
        for bar in self._bars:
            yield bar
            await asyncio.sleep(delay_seconds)

