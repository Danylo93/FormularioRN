import argparse
import asyncio
from datetime import datetime
from typing import Optional

from config import Settings
from forex_ai.backtest.runner import run_backtest
from forex_ai.api.server import run_api
from forex_ai.screener.runner import screen_pairs
from forex_ai.news.source import load_news_csv
from forex_ai.news.filter import NewsFilter
from forex_ai.news.tradingeconomics import fetch_te_events
import subprocess
from forex_ai.data.streamer import ReplayStreamer
from forex_ai.signals.engine import build_default_engine
from forex_ai.broker.paper import PaperBroker


def parse_timeframe(tf: str) -> str:
    allowed = {"1m", "5m", "15m", "30m", "1h", "4h", "1d"}
    if tf not in allowed:
        raise argparse.ArgumentTypeError(f"Timeframe inválido: {tf}")
    return tf


def main():
    parser = argparse.ArgumentParser(description="Forex AI Dow + Fibonacci")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_back = sub.add_parser("backtest", help="Executa backtest com dados do Yahoo Finance")
    p_back.add_argument("--symbol", required=True)
    p_back.add_argument("--start", required=True)
    p_back.add_argument("--end", required=True)
    p_back.add_argument("--timeframe", type=parse_timeframe, default="15m")

    p_rt = sub.add_parser("realtime", help="Roda streamer em replay e imprime sinais")
    p_rt.add_argument("--symbol", required=True)
    p_rt.add_argument("--timeframe", type=parse_timeframe, default="15m")

    p_api = sub.add_parser("api", help="Inicia API com streamer em replay")
    p_scr = sub.add_parser("screener", help="Executa screener multi-par")
    p_scr.add_argument("--timeframe", type=parse_timeframe, default="15m")
    p_scr.add_argument("--news_csv", help="Caminho CSV de notícias (opcional)")
    p_scr.add_argument("--te_key", help="TradingEconomics API key (opcional)")
    p_scr.add_argument("--avoid_news", action="store_true")
    p_api.add_argument("--symbol", required=True)
    p_api.add_argument("--timeframe", type=parse_timeframe, default="15m")
    p_api.add_argument("--host", default="0.0.0.0")
    p_api.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.cmd == "backtest":
        settings = Settings(symbol=args.symbol, timeframe=args.timeframe)
        run_backtest(settings, start=args.start, end=args.end)
        return

    if args.cmd == "realtime":
        settings = Settings(symbol=args.symbol, timeframe=args.timeframe)
        engine = build_default_engine(settings)
        broker = PaperBroker(settings)
        streamer = ReplayStreamer(settings)

        async def run():
            async for bar in streamer.stream():
                signal = engine.on_bar(bar)
                if signal is not None:
                    order = broker.place_order(signal)
                    print({
                        "time": bar.end_time.isoformat(),
                        "signal": signal.as_dict(),
                        "order": order.as_dict(),
                    })
                broker.on_bar(bar)

        asyncio.run(run())
        return

    if args.cmd == "api":
        settings = Settings(symbol=args.symbol, timeframe=args.timeframe)
        run_api(settings, host=args.host, port=args.port)
        return

    if args.cmd == "frontend":
        # Executa o app do Streamlit
        subprocess.run(["streamlit", "run", "src/forex_ai/frontend/app.py"], check=False)
        return

    if args.cmd == "screener":
        nf = None
        if getattr(args, "news_csv", None):
            events = load_news_csv(args.news_csv)
            nf = NewsFilter(events)
        if getattr(args, "te_key", None):
            te_events = fetch_te_events(args.te_key, countries=["USA", "EUR", "GBR", "JPN", "CAN", "AUS", "NZL", "CHN"], impact_levels=["high"])
            nf = NewsFilter(te_events)
        opps = screen_pairs(timeframe=args.timeframe, news_filter=nf if args.avoid_news else None)
        for o in opps[:20]:
            print(o.__dict__)


if __name__ == "__main__":
    main()

