"""Database module for handling SQLite operations"""
import aiosqlite
import os
from typing import List, Dict, Optional, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "appdata.db")


async def get_db():
    """Get database connection"""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Initialize database with required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    db = await get_db()
    try:
        # Create users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL
            )
        """)

        # Create items table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                access_token TEXT NOT NULL,
                transaction_cursor TEXT,
                bank_name TEXT,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        # Create accounts table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                item_id TEXT NOT NULL,
                name TEXT,
                FOREIGN KEY(item_id) REFERENCES items(id)
            )
        """)

        # Create transactions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                account_id TEXT NOT NULL,
                category TEXT,
                date TEXT,
                authorized_date TEXT,
                name TEXT,
                amount REAL,
                currency_code TEXT,
                pending_transaction_id TEXT,
                is_removed INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            )
        """)

        await db.commit()
    finally:
        await db.close()


# User functions
async def add_user(user_id: str, username: str) -> Dict[str, str]:
    """Add a new user"""
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO users (id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()
        return {"id": user_id, "username": username}
    finally:
        await db.close()


async def get_user_list() -> List[Dict[str, str]]:
    """Get all users"""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id, username FROM users")
        rows = await cursor.fetchall()
        return [{"id": row["id"], "username": row["username"]} for row in rows]
    finally:
        await db.close()


async def get_user_record(user_id: str) -> Optional[Dict[str, str]]:
    """Get a single user record"""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id, username FROM users WHERE id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {"id": row["id"], "username": row["username"]}
        return None
    finally:
        await db.close()


# Item functions
async def add_item(item_id: str, user_id: str, access_token: str) -> Dict[str, str]:
    """Add a new item (bank connection)"""
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO items (id, user_id, access_token) VALUES (?, ?, ?)",
            (item_id, user_id, access_token)
        )
        await db.commit()
        return {"id": item_id, "user_id": user_id, "access_token": access_token}
    finally:
        await db.close()


async def add_bank_name_for_item(item_id: str, institution_name: str):
    """Update the bank name for an item"""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE items SET bank_name = ? WHERE id = ?",
            (institution_name, item_id)
        )
        await db.commit()
    finally:
        await db.close()


async def get_items_for_user(user_id: str) -> List[Dict[str, Any]]:
    """Get all items for a user"""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id, access_token, transaction_cursor FROM items WHERE user_id = ? AND is_active = 1",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": row["id"],
                "access_token": row["access_token"],
                "transaction_cursor": row["transaction_cursor"]
            }
            for row in rows
        ]
    finally:
        await db.close()


async def get_item_info(item_id: str) -> Optional[Dict[str, Any]]:
    """Get item info by item_id"""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id, access_token, transaction_cursor FROM items WHERE id = ?",
            (item_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "access_token": row["access_token"],
                "transaction_cursor": row["transaction_cursor"]
            }
        return None
    finally:
        await db.close()


async def get_item_info_for_user(item_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get item info for a specific user"""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id, access_token, transaction_cursor FROM items WHERE id = ? AND user_id = ?",
            (item_id, user_id)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "access_token": row["access_token"],
                "transaction_cursor": row["transaction_cursor"]
            }
        return None
    finally:
        await db.close()


async def get_bank_names_for_user(user_id: str) -> List[Dict[str, str]]:
    """Get all bank names for a user"""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id, bank_name FROM items WHERE user_id = ? AND is_active = 1",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [{"id": row["id"], "name": row["bank_name"]} for row in rows]
    finally:
        await db.close()


async def deactivate_item(item_id: str):
    """Deactivate an item"""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE items SET is_active = 0 WHERE id = ?",
            (item_id,)
        )
        await db.commit()
    finally:
        await db.close()


async def save_cursor_for_item(cursor: str, item_id: str):
    """Save the transaction cursor for an item"""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE items SET transaction_cursor = ? WHERE id = ?",
            (cursor, item_id)
        )
        await db.commit()
    finally:
        await db.close()


# Account functions
async def add_account(account_id: str, item_id: str, account_name: str):
    """Add a new account"""
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO accounts (id, item_id, name) VALUES (?, ?, ?)",
            (account_id, item_id, account_name)
        )
        await db.commit()
    finally:
        await db.close()


async def get_account_ids_for_item(item_id: str) -> List[str]:
    """Get all account IDs for an item"""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id FROM accounts WHERE item_id = ?",
            (item_id,)
        )
        rows = await cursor.fetchall()
        return [row["id"] for row in rows]
    finally:
        await db.close()


# Transaction functions
async def add_new_transaction(transaction: Dict[str, Any]):
    """Add a new transaction"""
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO transactions
            (id, user_id, account_id, category, date, authorized_date, name, amount, currency_code, pending_transaction_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                transaction["id"],
                transaction["user_id"],
                transaction["account_id"],
                transaction["category"],
                transaction["date"],
                transaction["authorized_date"],
                transaction["name"],
                transaction["amount"],
                transaction["currency_code"],
                transaction["pending_transaction_id"]
            )
        )
        await db.commit()
    finally:
        await db.close()


async def modify_existing_transaction(transaction: Dict[str, Any]):
    """Modify an existing transaction"""
    db = await get_db()
    try:
        await db.execute(
            """UPDATE transactions
            SET account_id = ?, category = ?, date = ?, authorized_date = ?,
                name = ?, amount = ?, currency_code = ?, pending_transaction_id = ?
            WHERE id = ?""",
            (
                transaction["account_id"],
                transaction["category"],
                transaction["date"],
                transaction["authorized_date"],
                transaction["name"],
                transaction["amount"],
                transaction["currency_code"],
                transaction["pending_transaction_id"],
                transaction["id"]
            )
        )
        await db.commit()
    finally:
        await db.close()


async def mark_transaction_as_removed(transaction_id: str):
    """Mark a transaction as removed"""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE transactions SET is_removed = 1 WHERE id = ?",
            (transaction_id,)
        )
        await db.commit()
    finally:
        await db.close()


async def delete_existing_transaction(transaction_id: str):
    """Delete a transaction"""
    db = await get_db()
    try:
        await db.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )
        await db.commit()
    finally:
        await db.close()


async def get_transactions_for_user(user_id: str, max_count: int = 50) -> List[Dict[str, Any]]:
    """Get transactions for a user"""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT t.*, a.name as account_name, i.bank_name
            FROM transactions t
            LEFT JOIN accounts a ON t.account_id = a.id
            LEFT JOIN items i ON a.item_id = i.id
            WHERE t.user_id = ? AND t.is_removed = 0
            ORDER BY date DESC
            LIMIT ?""",
            (user_id, max_count)
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "account_id": row["account_id"],
                "category": row["category"],
                "date": row["date"],
                "authorized_date": row["authorized_date"],
                "name": row["name"],
                "amount": row["amount"],
                "currency_code": row["currency_code"],
                "pending_transaction_id": row["pending_transaction_id"],
                "account_name": row["account_name"],
                "bank_name": row["bank_name"]
            }
            for row in rows
        ]
    finally:
        await db.close()
