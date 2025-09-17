from __future__ import annotations

# Stub para futura integração com OANDA REST/Stream API.
# Prever uso de env vars: OANDA_API_KEY, OANDA_ACCOUNT_ID, OANDA_ENV (practice/live)

class OandaAdapter:
    def __init__(self, api_key: str, account_id: str, env: str = "practice"):
        self.api_key = api_key
        self.account_id = account_id
        self.env = env

    def stream(self, symbol: str, timeframe: str):
        raise NotImplementedError("OandaAdapter.stream não implementado neste exemplo.")

