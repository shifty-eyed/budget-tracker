"""Token routes for Plaid Link"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import html
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest

from server.plaid_client import plaid_client
from server import db
from server.utils import get_logged_in_user_id

router = APIRouter()


class GenerateLinkTokenRequest(BaseModel):
    userId: str


class ExchangePublicTokenRequest(BaseModel):
    publicToken: str


async def populate_bank_name(access_token: str, item_id: str):
    """Populate the bank name for an item"""
    try:
        # Get institution ID from the item
        from plaid.model.item_get_request import ItemGetRequest
        request = ItemGetRequest(access_token=access_token)
        response = plaid_client.item_get(request)
        institution_id = response['item']['institution_id']

        # Get institution details
        inst_request = InstitutionsGetByIdRequest(
            institution_id=institution_id,
            country_codes=[CountryCode("US")]
        )
        inst_response = plaid_client.institutions_get_by_id(inst_request)
        institution_name = inst_response['institution']['name']

        await db.add_bank_name_for_item(item_id, institution_name)
    except Exception as e:
        print(f"Error populating bank name: {e}")


async def populate_account_names(access_token: str, item_id: str):
    """Populate account names for an item"""
    try:
        request = AccountsGetRequest(access_token=access_token)
        response = plaid_client.accounts_get(request)

        for account in response['accounts']:
            await db.add_account(
                account['account_id'],
                item_id,
                account['name']
            )
    except Exception as e:
        print(f"Error populating account names: {e}")


@router.post("/generate_link_token")
async def generate_link_token(request: GenerateLinkTokenRequest):
    """Generate a Plaid Link token"""
    user_id = request.userId

    try:
        link_request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="Budget Tracker",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en"
        )

        response = plaid_client.link_token_create(link_request)
        return {"linkToken": response['link_token']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exchange_public_token")
async def exchange_public_token(
    request: ExchangePublicTokenRequest,
    user_id: str = Depends(get_logged_in_user_id)
):
    """Exchange public token for access token"""
    public_token = html.escape(request.publicToken)

    try:
        # Exchange public token
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        exchange_response = plaid_client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        # Store in database
        await db.add_item(item_id, user_id, access_token)

        # Populate bank name and account names
        await populate_bank_name(access_token, item_id)
        await populate_account_names(access_token, item_id)

        # Trigger initial transaction sync
        from server.routes.transactions import sync_transactions
        await sync_transactions(item_id, user_id)

        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
