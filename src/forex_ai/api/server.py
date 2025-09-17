from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import Optional

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

from config import Settings
from ..data.streamer import ReplayStreamer
from ..signals.engine import build_default_engine
from ..broker.paper import PaperBroker


class SignalOut(BaseModel):
    symbol: str
    timeframe: str
    side: str
    entry: float
    stop: float
    tp1: float
    tp2: float
    size: float
    reason: str


def make_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="Forex AI Dow + Fibonacci")
    engine = build_default_engine(settings)
    broker = PaperBroker(settings)
    streamer = ReplayStreamer(settings)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/equity")
    def equity():
        return {"equity": broker.equity}

    @app.get("/positions")
    def positions():
        return [p.as_dict() for p in broker.positions]

    @app.websocket("/ws")
    async def ws(ws: WebSocket):
        await ws.accept()
        async for bar in streamer.stream():
            signal = engine.on_bar(bar)
            payload = {"bar": {
                "time": bar.end_time.isoformat(),
                "close": bar.close,
            }}
            if signal is not None:
                order = broker.place_order(signal)
                payload["signal"] = signal.as_dict()
                payload["order"] = order.as_dict()
            await ws.send_json(payload)
            broker.on_bar(bar)

    return app


def run_api(settings: Settings, host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    app = make_app(settings)
    uvicorn.run(app, host=host, port=port)

