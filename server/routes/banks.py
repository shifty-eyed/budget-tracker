"""Bank routes"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from plaid.model.item_remove_request import ItemRemoveRequest

from server.plaid_client import plaid_client
from server import db
from server.utils import get_logged_in_user_id

router = APIRouter()


class DeactivateBankRequest(BaseModel):
    itemId: str


@router.get("/list")
async def list_banks(user_id: str = Depends(get_logged_in_user_id)):
    """List all banks for a user"""
    return await db.get_bank_names_for_user(user_id)


@router.post("/deactivate")
async def deactivate_bank(
    request: DeactivateBankRequest,
    user_id: str = Depends(get_logged_in_user_id)
):
    """Deactivate a bank connection"""
    try:
        # Get item info
        item_info = await db.get_item_info_for_user(request.itemId, user_id)
        if not item_info:
            raise HTTPException(status_code=404, detail="Item not found")

        # Remove from Plaid
        remove_request = ItemRemoveRequest(
            access_token=item_info["access_token"]
        )
        plaid_client.item_remove(remove_request)

        # Deactivate in database
        await db.deactivate_item(request.itemId)

        return {"removed": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
