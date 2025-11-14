from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest as PlaidLinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

from .config import get_settings
from .plaid_client import create_plaid_client, format_error
from .schemas import (
    LinkTokenCreateRequest,
    LinkTokenCreateResponse,
    PublicTokenExchangeRequest,
    PublicTokenExchangeResponse,
    TransactionsResponse,
)
from .storage import store

settings = get_settings()
app = FastAPI(title=settings.application_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = create_plaid_client()


def _plaid_country_codes() -> List[CountryCode]:
    return [CountryCode(code) for code in settings.plaid_country_codes]


def _plaid_products() -> List[Products]:
    return [Products(product) for product in settings.plaid_products]


@app.get("/api/health")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/create_link_token", response_model=LinkTokenCreateResponse)
def create_link_token(payload: LinkTokenCreateRequest) -> LinkTokenCreateResponse:
    try:
        request = PlaidLinkTokenCreateRequest(
            products=_plaid_products(),
            client_name=settings.application_name,
            country_codes=_plaid_country_codes(),
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id=payload.user_id),
        )
        if settings.plaid_redirect_uri:
            request.redirect_uri = settings.plaid_redirect_uri
        if settings.plaid_android_package_name:
            request.android_package_name = settings.plaid_android_package_name
        if settings.webhook_url:
            request.webhook = settings.webhook_url
        response = client.link_token_create(request)
        return LinkTokenCreateResponse(link_token=response.link_token)
    except Exception as err:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=format_error(err)) from err


@app.post("/api/set_access_token", response_model=PublicTokenExchangeResponse)
def exchange_public_token(payload: PublicTokenExchangeRequest) -> PublicTokenExchangeResponse:
    try:
        request = ItemPublicTokenExchangeRequest(public_token=payload.public_token)
        exchange_response = client.item_public_token_exchange(request)
        access_token = exchange_response.access_token
        item_id = exchange_response.item_id
        store.upsert_item(payload.user_id, access_token=access_token, item_id=item_id)
        return PublicTokenExchangeResponse(access_token=access_token, item_id=item_id)
    except Exception as err:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=format_error(err)) from err


@app.get("/api/transactions", response_model=TransactionsResponse)
def get_transactions(user_id: str, days: int = 30) -> TransactionsResponse:
    state = store.get_item(user_id)
    if not state.access_token:
        raise HTTPException(status_code=400, detail="No access token on file for this user")

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    try:
        request = TransactionsGetRequest(
            access_token=state.access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(count=100),
        )
        response = client.transactions_get(request)
        transactions = list(response.transactions)
        while len(transactions) < response.total_transactions:
            request = TransactionsGetRequest(
                access_token=state.access_token,
                start_date=start_date,
                end_date=end_date,
                options=TransactionsGetRequestOptions(
                    count=100,
                    offset=len(transactions),
                ),
            )
            page = client.transactions_get(request)
            transactions.extend(page.transactions)
        transaction_dicts = [transaction.to_dict() for transaction in transactions]
        return TransactionsResponse(transactions=transaction_dicts)
    except Exception as err:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=format_error(err)) from err
