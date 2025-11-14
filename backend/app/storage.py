from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Dict, Optional


@dataclass
class ItemState:
    access_token: Optional[str] = None
    item_id: Optional[str] = None
    cursor: Optional[str] = None


class InMemoryStore:
    def __init__(self) -> None:
        self._items: Dict[str, ItemState] = {}
        self._lock = Lock()

    def upsert_item(self, user_id: str, *, access_token: str, item_id: str) -> ItemState:
        with self._lock:
            state = self._items.setdefault(user_id, ItemState())
            state.access_token = access_token
            state.item_id = item_id
            return state

    def get_item(self, user_id: str) -> ItemState:
        with self._lock:
            return self._items.setdefault(user_id, ItemState())

    def set_cursor(self, user_id: str, cursor: Optional[str]) -> None:
        with self._lock:
            state = self._items.setdefault(user_id, ItemState())
            state.cursor = cursor


store = InMemoryStore()
