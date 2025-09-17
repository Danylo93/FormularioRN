## Forex AI Dow + Fibonacci (PT-BR)

Sistema completo de análise e geração de sinais para Forex em tempo real (ou replay), combinando:
- Teoria de Dow (tendência via swings HH/HL vs LH/LL)
- IA online (SGDClassifier) com features de preço/volatilidade
- Stops técnicos (último swing) e 2 alvos por Fibonacci (1.618 e 2.618)
- Paper trading com execução, SL/TP e métricas
- API FastAPI (REST e WebSocket) e CLI

### Instalação

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Uso Rápido

- Backtest com dados do Yahoo (replay):
```bash
PYTHONPATH=src python src/cli.py backtest --symbol EURUSD=X --start 2023-01-01 --end 2023-03-01 --timeframe 15m
```

- Executar API (REST/WebSocket) com streamer em replay:
```bash
PYTHONPATH=src python src/cli.py api --symbol EURUSD=X --timeframe 15m
```

- Frontend (Streamlit):
```bash
PYTHONPATH=src python src/cli.py frontend
```

- Executar somente streamer/sinais em console (replay):
```bash
PYTHONPATH=src python src/cli.py realtime --symbol EURUSD=X --timeframe 15m
```

Observação: para corretoras reais (ex: OANDA), adapte as credenciais em variáveis de ambiente e implemente o adapter.

### Estrutura

```
src/
  cli.py
  config.py
  forex_ai/
    data/
    features/
    model/
    signals/
    broker/
    backtest/
    api/
    frontend/
```

### Avisos

- Código para fins educacionais. Não é recomendação de investimento.
- Avalie custos de slippage, spreads e execução real.

