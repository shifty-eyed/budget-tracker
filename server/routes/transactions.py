"""Transaction routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import asyncio
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.api_client import ApiException

from server.plaid_client import plaid_client
from server import db
from server.utils import get_logged_in_user_id
from server.simple_transaction import SimpleTransaction

router = APIRouter()


async def fetch_new_sync_data(access_token: str, cursor: Optional[str] = None):
    """Fetch new transaction sync data from Plaid with retry logic"""
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor if cursor else ""
            )
            response = plaid_client.transactions_sync(request)
            return {
                "added": response.get('added', []),
                "modified": response.get('modified', []),
                "removed": response.get('removed', []),
                "next_cursor": response.get('next_cursor'),
                "has_more": response.get('has_more', False)
            }
        except ApiException as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise e
            await asyncio.sleep(1)


async def sync_transactions(item_id: str, user_id: str):
    """Sync transactions for a specific item"""
    summary = {"added": 0, "modified": 0, "removed": 0}

    try:
        # Get item info
        item_info = await db.get_item_info(item_id)
        if not item_info:
            return summary

        access_token = item_info["access_token"]
        cursor = item_info["transaction_cursor"]

        has_more = True
        while has_more:
            # Fetch new sync data
            sync_data = await fetch_new_sync_data(access_token, cursor)

            # Add new transactions
            for trans in sync_data["added"]:
                simple_trans = SimpleTransaction.from_plaid_transaction(trans, user_id)
                await db.add_new_transaction(simple_trans.to_dict())
                summary["added"] += 1

            # Modify existing transactions
            for trans in sync_data["modified"]:
                simple_trans = SimpleTransaction.from_plaid_transaction(trans, user_id)
                await db.modify_existing_transaction(simple_trans.to_dict())
                summary["modified"] += 1

            # Mark removed transactions
            for removed in sync_data["removed"]:
                await db.mark_transaction_as_removed(removed['transaction_id'])
                summary["removed"] += 1

            # Update cursor
            cursor = sync_data["next_cursor"]
            has_more = sync_data["has_more"]

        # Save the cursor
        await db.save_cursor_for_item(cursor, item_id)

        return summary
    except Exception as e:
        print(f"Error syncing transactions: {e}")
        return summary


@router.post("/sync")
async def sync_all_transactions(user_id: str = Depends(get_logged_in_user_id)):
    """Sync transactions for all items for a user"""
    try:
        # Get all items for user
        items = await db.get_items_for_user(user_id)

        # Sync transactions for each item
        results = await asyncio.gather(
            *[sync_transactions(item["id"], user_id) for item in items]
        )

        # Aggregate results
        total_summary = {"added": 0, "modified": 0, "removed": 0}
        for result in results:
            total_summary["added"] += result["added"]
            total_summary["modified"] += result["modified"]
            total_summary["removed"] += result["removed"]

        return total_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_transactions(
    maxCount: Optional[int] = 50,
    user_id: str = Depends(get_logged_in_user_id)
):
    """List transactions for a user"""
    try:
        transactions = await db.get_transactions_for_user(user_id, maxCount)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
