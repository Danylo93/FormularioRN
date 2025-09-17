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

### Rodando com Docker

```bash
docker compose up --build
```

- Frontend: `http://localhost:8501`
- API: `http://localhost:8000`

Autenticação (necessária para endpoints protegidos):
```bash
curl -X POST 'http://localhost:8000/auth/token?user_id=demo&user_type=1'
# => {"access_token":"<JWT>"}
```

Atualizar notícias (TradingEconomics) no servidor (opcional):
```bash
curl -X POST 'http://localhost:8000/news/refresh?te_api_key=<TE_KEY>&countries=USA,EUR,GBR,JPN,CAN,AUS,NZL,CHN&impact=high' \
  -H "Authorization: Bearer <JWT>"
```

Screener via API (retorna oportunidades com RR e stops/alvos):
```bash
curl 'http://localhost:8000/screener?timeframe=15m&rr_min=1.3&align=true&top_n=15&avoid_news=true' \
  -H "Authorization: Bearer <JWT>"
```

WebSocket (sinais em tempo real/replay):
- Conecte em `ws://localhost:8000/ws`. Exemplo Python:
```python
import asyncio, websockets, json

async def run():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if 'signal' in data:
                print('SIGNAL:', data['signal'])

asyncio.run(run())
```

Frontend (Streamlit):
- Acesse `http://localhost:8501`, informe `API URL` (ex.: `http://localhost:8000`), clique em "Login/API Token", atualize notícias se desejar, e use "Executar Busca" no tab Screener.

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

### Como testar e pegar sinais (resumo)

- CLI (replay simples no console):
```bash
PYTHONPATH=src python src/cli.py realtime --symbol EURUSD=X --timeframe 15m
```
Imprime objetos com `signal` e `order` quando houver entradas.

- API REST (screener):
```bash
curl -H "Authorization: Bearer <JWT>" \
  'http://localhost:8000/screener?timeframe=15m&rr_min=1.4&align=true&top_n=20&avoid_news=true'
```

- WebSocket (tempo real/replay):
```bash
wscat -c ws://localhost:8000/ws
```
Quando um sinal ocorrer, a mensagem conterá uma chave `signal` com `entry`, `stop`, `tp1`, `tp2` e `size`.

### Notas sobre dados (Yahoo Finance)

- Os tickers de Forex no Yahoo usam sufixo `=X` (ex.: `EURUSD=X`, `GBPUSD=X`).
- Em alguns ambientes (rede/containers) o Yahoo pode falhar/limitar, resultando em erros `YFTzMissingError`.
- Alternativas:
  - Rode localmente com `PYTHONPATH=src` fora do Docker para testar.
  - Use o frontend para visualizar um par por vez (pode ser mais tolerante a limites).
  - Carregue dados próprios via CSV (colunas: `time, open, high, low, close, volume`) e adapte o screener para usar `forex_ai.data.csv_source.load_csv_bars`.
  - Integre outra fonte (ex.: OANDA) no adapter `forex_ai/data/oanda.py`.

