from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import Optional

from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import Settings
from ..data.streamer import ReplayStreamer
from ..signals.engine import build_default_engine
from ..broker.paper import PaperBroker
from ..screener.runner import screen_pairs
from .auth import create_jwt, require_auth
from ..news.filter import NewsFilter
from ..news.tradingeconomics import fetch_te_events


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    news_filter_ref: dict[str, NewsFilter | None] = {"nf": None}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/auth/token")
    def auth_token(user_id: str = "demo", user_type: int = 1):
        return {"access_token": create_jwt(user_id=user_id, user_type=user_type)}

    @app.get("/equity")
    def equity(_: dict = Depends(require_auth)):
        return {"equity": broker.equity}

    @app.get("/positions")
    def positions(_: dict = Depends(require_auth)):
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

    @app.post("/news/refresh")
    def refresh_news(te_api_key: str, countries: str = "USA,EUR,GBR,JPN,CAN,AUS,NZL,CHN", impact: str = "high"):
        try:
            countries_list = [c.strip() for c in countries.split(",") if c.strip()]
            impact_list = [impact.strip().lower()]
            events = fetch_te_events(api_key=te_api_key, countries=countries_list, impact_levels=impact_list)
            nf = NewsFilter(events)
            news_filter_ref["nf"] = nf
            return {"loaded": len(events)}
        except Exception as e:
            return {"error": str(e)}

    @app.get("/screener")
    def screener(timeframe: str | None = None, rr_min: float = 1.2, align: bool = True, top_n: int = 20, avoid_news: bool = True, _: dict = Depends(require_auth)):
        tf = timeframe or settings.timeframe
        nf = news_filter_ref["nf"] if avoid_news else None
        opps = screen_pairs(timeframe=tf, rr_min=rr_min, align_m5_m15=align, top_n=top_n, news_filter=nf)
        return [op.__dict__ for op in opps]

    return app


def run_api(settings: Settings, host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    app = make_app(settings)
    uvicorn.run(app, host=host, port=port)

