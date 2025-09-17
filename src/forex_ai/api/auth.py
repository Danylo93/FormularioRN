from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_SECRET = "change-me"  # use env var em produção
JWT_ALG = "HS256"
security = HTTPBearer(auto_error=False)


def create_jwt(user_id: str, user_type: int = 1, ttl_minutes: int = 60) -> str:
    payload = {
        "sub": user_id,
        "user_type": user_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def verify_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")


def require_auth(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if creds is None or not creds.scheme.lower() == "bearer":
        raise HTTPException(status_code=401, detail="Authorization Bearer requerido")
    return verify_jwt(creds.credentials)

