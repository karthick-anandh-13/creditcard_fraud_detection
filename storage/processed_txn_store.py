# storage/processed_txn_store.py

from datetime import datetime
from storage.mongo import db


class ProcessedTransactionStore:
    """
    Ensures idempotency & replay protection.
    Each transaction_id is processed exactly once.
    """

    def __init__(self):
        self.col = db["processed_transactions"]
        self.col.create_index("transaction_id", unique=True)

    def is_processed(self, transaction_id: str) -> bool:
        return self.col.find_one(
            {"transaction_id": transaction_id},
            {"_id": 1}
        ) is not None

    def mark_processed(
        self,
        transaction_id: str,
        decision: str,
        source: str = "UPI_CONSUMER"
    ):
        self.col.insert_one({
            "transaction_id": transaction_id,
            "decision": decision,
            "source": source,
            "processed_at": datetime.utcnow()
        })
