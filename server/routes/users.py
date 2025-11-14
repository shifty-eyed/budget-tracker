"""User routes"""
from fastapi import APIRouter, Response, Cookie
from pydantic import BaseModel
from typing import Optional
import uuid
import html

from server import db

router = APIRouter()


class CreateUserRequest(BaseModel):
    username: str


class SignInRequest(BaseModel):
    userId: str


@router.post("/create")
async def create_user(request: CreateUserRequest, response: Response):
    """Create a new user"""
    username = html.escape(request.username)
    user_id = str(uuid.uuid4())

    result = await db.add_user(user_id, username)

    # Set cookie
    response.set_cookie(
        key="signedInUser",
        value=user_id,
        max_age=30 * 24 * 60 * 60,  # 30 days
        httponly=True
    )

    return result


@router.get("/list")
async def get_user_list():
    """Get list of all users"""
    return await db.get_user_list()


@router.post("/sign_in")
async def sign_in(request: SignInRequest, response: Response):
    """Sign in a user"""
    response.set_cookie(
        key="signedInUser",
        value=request.userId,
        max_age=30 * 24 * 60 * 60,  # 30 days
        httponly=True
    )
    return {"signedIn": True}


@router.post("/sign_out")
async def sign_out(response: Response):
    """Sign out a user"""
    response.delete_cookie("signedInUser")
    return {"signedOut": True}


@router.get("/get_my_info")
async def get_my_info(signedInUser: Optional[str] = Cookie(default=None)):
    """Get current user info"""
    if not signedInUser:
        return {"userId": None, "username": None}

    user = await db.get_user_record(signedInUser)
    if user:
        return {"userId": user["id"], "username": user["username"]}
    return {"userId": None, "username": None}
