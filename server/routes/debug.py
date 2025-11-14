"""Debug routes"""
from fastapi import APIRouter, HTTPException, Depends
import random
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
from plaid.model.webhook_type import WebhookType

from server.plaid_client import plaid_client
from server import db
from server.utils import get_logged_in_user_id

router = APIRouter()


@router.post("/run")
async def debug_run(user_id: str = Depends(get_logged_in_user_id)):
    """Debug endpoint for running custom code"""
    # This is a simple endpoint for running debug code
    # In production, this should be removed or properly secured
    return {"done": True}


@router.post("/generate_webhook")
async def generate_webhook(user_id: str = Depends(get_logged_in_user_id)):
    """Generate a test webhook in sandbox mode"""
    try:
        # Get all items for user
        items = await db.get_items_for_user(user_id)

        if not items:
            raise HTTPException(status_code=404, detail="No items found")

        # Pick a random item
        random_item = random.choice(items)
        access_token = random_item["access_token"]

        # Fire webhook
        request = SandboxItemFireWebhookRequest(
            access_token=access_token,
            webhook_code="SYNC_UPDATES_AVAILABLE",
            webhook_type=WebhookType("TRANSACTIONS")
        )
        plaid_client.sandbox_item_fire_webhook(request)

        return {"fired": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
