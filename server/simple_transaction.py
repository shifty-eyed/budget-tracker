"""Simple transaction object to represent data from Plaid transactions"""
from typing import Optional, Dict, Any


class SimpleTransaction:
    """
    A simple object to pass to our database functions that represents
    the data our application cares about from the Plaid transaction endpoint
    """

    def __init__(
        self,
        id: str,
        user_id: str,
        account_id: str,
        category: str,
        date: str,
        authorized_date: Optional[str],
        name: str,
        amount: float,
        currency_code: str,
        pending_transaction_id: Optional[str]
    ):
        self.id = id
        self.user_id = user_id
        self.account_id = account_id
        self.category = category
        self.date = date
        self.authorized_date = authorized_date
        self.name = name
        self.amount = amount
        self.currency_code = currency_code
        self.pending_transaction_id = pending_transaction_id

    @staticmethod
    def from_plaid_transaction(transaction: Any, user_id: str) -> 'SimpleTransaction':
        """Create a SimpleTransaction from a Plaid transaction object"""
        return SimpleTransaction(
            id=transaction.transaction_id,
            user_id=user_id,
            account_id=transaction.account_id,
            category=", ".join(transaction.personal_finance_category.primary) if transaction.personal_finance_category else "",
            date=str(transaction.date),
            authorized_date=str(transaction.authorized_date) if transaction.authorized_date else None,
            name=transaction.merchant_name or transaction.name,
            amount=transaction.amount,
            currency_code=transaction.iso_currency_code or "USD",
            pending_transaction_id=transaction.pending_transaction_id
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database operations"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_id": self.account_id,
            "category": self.category,
            "date": self.date,
            "authorized_date": self.authorized_date,
            "name": self.name,
            "amount": self.amount,
            "currency_code": self.currency_code,
            "pending_transaction_id": self.pending_transaction_id
        }
