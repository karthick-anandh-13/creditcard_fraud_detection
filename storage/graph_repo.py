from datetime import datetime
from storage.mongo import db

class GraphStore:
    def __init__(self):
        self.col = db["upi_graph_edges"]

    def record_transaction(
        self,
        payer_vpa: str,
        payee_vpa: str,
        amount: float,
        timestamp: datetime
    ):
        self.col.update_one(
            {"payer_vpa": payer_vpa, "payee_vpa": payee_vpa},
            {
                "$inc": {
                    "count": 1,
                    "total_amount": amount
                },
                "$set": {
                    "last_seen": timestamp
                }
            },
            upsert=True
        )

    def get_edge_stats(self, payer_vpa: str, payee_vpa: str):
        return self.col.find_one(
            {"payer_vpa": payer_vpa, "payee_vpa": payee_vpa},
            {"_id": 0}
        )

    def get_unique_payees(self, payer_vpa: str) -> int:
        return self.col.count_documents({"payer_vpa": payer_vpa})

    def get_unique_payers(self, payee_vpa: str) -> int:
        return self.col.count_documents({"payee_vpa": payee_vpa})
