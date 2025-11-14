from __future__ import annotations

from pydantic import BaseModel


class LinkTokenCreateRequest(BaseModel):
    user_id: str


class LinkTokenCreateResponse(BaseModel):
    link_token: str


class PublicTokenExchangeRequest(BaseModel):
    public_token: str
    user_id: str


class PublicTokenExchangeResponse(BaseModel):
    access_token: str
    item_id: str
