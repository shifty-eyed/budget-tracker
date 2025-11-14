from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class Transaction(BaseModel):
    transaction_id: str
    name: str
    amount: float
    date: date
    category: Optional[List[str]] = None
    pending: bool
    account_id: str

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class TransactionsResponse(BaseModel):
    transactions: List[Transaction]
    next_cursor: Optional[str] = None
