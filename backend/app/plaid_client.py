from __future__ import annotations

from typing import Any, Dict

from plaid import ApiClient, Configuration
from plaid.api import plaid_api
from plaid.exceptions import ApiException

from .config import get_settings


def create_plaid_client() -> plaid_api.PlaidApi:
    settings = get_settings()
    configuration = Configuration(
        host=getattr(Configuration.Host, settings.plaid_env.upper()),
        api_key={
            "clientId": settings.plaid_client_id,
            "secret": settings.plaid_secret,
        },
    )
    api_client = ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def format_error(err: Any) -> Dict[str, Any]:
    if isinstance(err, ApiException):
        try:
            body = err.body.decode("utf-8") if hasattr(err.body, "decode") else err.body
        except Exception:  # noqa: BLE001
            body = err.body
        return {"error": {"status_code": err.status, "body": body}}
    return {"error": str(err)}
