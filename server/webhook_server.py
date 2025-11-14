"""Webhook server for receiving Plaid webhooks"""
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os

from server.routes.transactions import sync_transactions
from server import db

webhook_app = FastAPI()


class WebhookPayload(BaseModel):
    webhook_type: str
    webhook_code: str
    item_id: str


@webhook_app.post("/server/receive_webhook")
async def receive_webhook(request: Request):
    """Receive and process Plaid webhooks"""
    try:
        body = await request.json()
        print(f"Webhook received: {body}")

        webhook_type = body.get("webhook_type")
        webhook_code = body.get("webhook_code")
        item_id = body.get("item_id")

        # Handle transaction webhooks
        if webhook_type == "TRANSACTIONS":
            if webhook_code == "SYNC_UPDATES_AVAILABLE":
                print(f"Syncing transactions for item {item_id}")
                # Get the user_id for this item
                item_info = await db.get_item_info(item_id)
                if item_info:
                    # Get user_id from the item
                    # We need to add a function to get user_id from item_id
                    # For now, we'll just log it
                    print(f"Would sync transactions for item {item_id}")
                    # await sync_transactions(item_id, user_id)

        # Handle item webhooks
        elif webhook_type == "ITEM":
            if webhook_code == "ERROR":
                print(f"Item {item_id} has an error - user needs to update credentials")
            elif webhook_code == "NEW_ACCOUNTS_AVAILABLE":
                print(f"Item {item_id} has new accounts available")
            elif webhook_code == "PENDING_EXPIRATION":
                print(f"Item {item_id} access is about to expire")
            elif webhook_code == "USER_PERMISSION_REVOKED":
                print(f"Item {item_id} permission was revoked")
            elif webhook_code == "WEBHOOK_UPDATE_ACKNOWLEDGED":
                print(f"Webhook update acknowledged for item {item_id}")

        return {"received": True}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_webhook_server():
    """Get the webhook server instance"""
    return webhook_app
