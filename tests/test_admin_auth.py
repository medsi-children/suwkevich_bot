import pytest
from fastapi import HTTPException

from app.services import admin_auth


def test_admin_routes_are_closed_without_configured_token(monkeypatch) -> None:
    monkeypatch.setattr(admin_auth.settings, "admin_api_token", "")
    with pytest.raises(HTTPException) as exc:
        admin_auth.require_admin_token("anything")
    assert exc.value.status_code == 404


def test_admin_routes_reject_wrong_token(monkeypatch) -> None:
    monkeypatch.setattr(admin_auth.settings, "admin_api_token", "expected")
    with pytest.raises(HTTPException) as exc:
        admin_auth.require_admin_token("wrong")
    assert exc.value.status_code == 403
    admin_auth.require_admin_token("expected")
