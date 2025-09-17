from dataclasses import dataclass


@dataclass
class Settings:
    symbol: str = "EURUSD=X"  # Ticker do Yahoo Finance (EURUSD=X)
    timeframe: str = "15m"     # {1m,5m,15m,30m,1h,4h,1d}

    # IA
    lookahead_bars: int = 5     # horizon de classificação de retorno futuro
    prob_threshold: float = 0.55

    # Gestão de risco
    risk_per_trade: float = 0.01   # 1% do capital
    initial_equity: float = 10000.0
    max_position_risk_fraction: float = 0.02

    # Dow theory pivots
    pivot_lookback: int = 3

    # Streamer (replay)
    history_bars: int = 1500

    # Backtest
    commission_perc: float = 0.0001  # 1 bps por trade

    # Notícias
    news_window_minutes: int = 30

