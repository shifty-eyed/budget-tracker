"""Utility functions"""
from fastapi import Cookie, HTTPException
from typing import Optional


def get_logged_in_user_id(signed_in_user: Optional[str] = Cookie(default=None)) -> str:
    """Get the logged in user ID from cookie"""
    if not signed_in_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return signed_in_user
