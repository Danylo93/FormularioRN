from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import requests

from .filter import NewsEvent


API_URL = "https://api.tradingeconomics.com/calendar"


def fetch_te_events(api_key: str, countries: Optional[List[str]] = None, impact_levels: Optional[List[str]] = None, 
                    start: Optional[str] = None, end: Optional[str] = None) -> List[NewsEvent]:
    params = {
        "c": api_key,
        "format": "json",
    }
    if countries:
        params["country"] = ",".join(countries)
    if start:
        params["d1"] = start
    if end:
        params["d2"] = end
    resp = requests.get(API_URL, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    events: List[NewsEvent] = []
    for item in data:
        try:
            # Campos típicos: Country, Category, Actual, Forecast, Previous, Date, Importance
            dt = item.get("Date") or item.get("DateUtc") or item.get("DateISO")
            when = datetime.fromisoformat(dt.replace("Z", "+00:00")) if isinstance(dt, str) else datetime.utcnow()
            currency = str(item.get("Currency") or item.get("Country") or "").upper()[:3]
            impact = str(item.get("Importance") or "").lower()
            title = str(item.get("Event") or item.get("Category") or "")
            if impact_levels and impact not in impact_levels:
                continue
            events.append(NewsEvent(time=when, currency=currency, impact=impact, title=title))
        except Exception:
            continue
    return events

