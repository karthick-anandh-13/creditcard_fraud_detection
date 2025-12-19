# state/graph_store.py

from datetime import datetime
from storage.mongo import db


class GraphStore:
    def __init__(self):
        self.col = db["transaction_graph"]

        # Indexes for fast graph queries
        self.col.create_index(
            [("payer_vpa", 1), ("payee_vpa", 1)],
            unique=True
        )
        self.col.create_index("payer_vpa")
        self.col.create_index("payee_vpa")

    # --------------------------------------------------
    # RECORD TRANSACTION EDGE
    # --------------------------------------------------
    def record_transaction(
        self,
        payer_vpa: str,
        payee_vpa: str,
        amount: float,
        timestamp: datetime
    ):
        self.col.update_one(
            {
                "payer_vpa": payer_vpa,
                "payee_vpa": payee_vpa
            },
            {
                "$inc": {
                    "count": 1,
                    "total_amount": amount
                },
                "$set": {
                    "last_seen": timestamp
                },
                "$setOnInsert": {
                    "created_at": timestamp
                }
            },
            upsert=True
        )

    # --------------------------------------------------
    # EDGE STATS (payer → payee)
    # --------------------------------------------------
    def get_edge_stats(self, payer_vpa: str, payee_vpa: str):
        doc = self.col.find_one(
            {
                "payer_vpa": payer_vpa,
                "payee_vpa": payee_vpa
            },
            {
                "_id": 0,
                "count": 1,
                "total_amount": 1,
                "last_seen": 1
            }
        )
        return doc

    # --------------------------------------------------
    # UNIQUE PAYEES PER PAYER
    # --------------------------------------------------
    def get_unique_payees(self, payer_vpa: str) -> int:
        return self.col.count_documents(
            {"payer_vpa": payer_vpa}
        )

    # --------------------------------------------------
    # UNIQUE PAYERS PER PAYEE
    # --------------------------------------------------
    def get_unique_payers(self, payee_vpa: str) -> int:
        return self.col.count_documents(
            {"payee_vpa": payee_vpa}
        )
