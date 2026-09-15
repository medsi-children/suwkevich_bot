from __future__ import annotations

import hmac
from typing import Annotated

from fastapi import Header, HTTPException

from app.core.config import settings


def require_admin_token(x_admin_token: Annotated[str | None, Header()] = None) -> None:
    expected = settings.admin_api_token.strip()
    if not expected:
        raise HTTPException(status_code=404, detail="Not found")
    if not x_admin_token or not hmac.compare_digest(x_admin_token, expected):
        raise HTTPException(status_code=403, detail="Forbidden")
