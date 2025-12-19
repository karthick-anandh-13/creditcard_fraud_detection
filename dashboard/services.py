from storage.mongo import db
from datetime import datetime, timedelta

# =====================================================
# COLLECTIONS
# =====================================================
audit_col = db["audit_decisions"]
risk_col = db["upi_risk_profiles"]
velocity_col = db["upi_velocity"]
graph_col = db["upi_graph_edges"]

# =====================================================
# GRAPH STORE (PERSISTENT)
# =====================================================
class GraphStore:
    def __init__(self):
        self.col = graph_col

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
                }
            },
            upsert=True
        )

    def get_edge_stats(self, payer_vpa: str, payee_vpa: str):
        return self.col.find_one(
            {
                "payer_vpa": payer_vpa,
                "payee_vpa": payee_vpa
            },
            {"_id": 0}
        )

    def get_unique_payees(self, payer_vpa: str) -> int:
        return self.col.count_documents({"payer_vpa": payer_vpa})

    def get_unique_payers(self, payee_vpa: str) -> int:
        return self.col.count_documents({"payee_vpa": payee_vpa})


# =====================================================
# OPS DASHBOARD ANALYTICS
# =====================================================
def get_recent_decisions(limit: int = 50):
    return list(
        audit_col
        .find({}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )


def get_risk_summary():
    total = audit_col.count_documents({})
    blocked = audit_col.count_documents({"decision": "BLOCK"})
    step_up = audit_col.count_documents({"decision": "STEP_UP_AUTH"})
    allowed = audit_col.count_documents({"decision": "ALLOW"})

    return {
        "total_transactions": total,
        "blocked": blocked,
        "step_up": step_up,
        "allowed": allowed,
        "block_rate": round(blocked / total, 4) if total else 0.0,
        "step_up_rate": round(step_up / total, 4) if total else 0.0
    }


def get_top_risky_users(limit: int = 10):
    return list(
        risk_col
        .find({}, {"_id": 0})
        .sort("risk_score", -1)
        .limit(limit)
    )


def get_velocity_alerts(threshold_1hr: int = 5):
    since = datetime.utcnow() - timedelta(hours=1)

    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": "$payer_vpa",
            "count": {"$sum": 1},
            "total_amount": {"$sum": "$amount"}
        }},
        {"$match": {"count": {"$gte": threshold_1hr}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]

    results = velocity_col.aggregate(pipeline)

    return [
        {
            "payer_vpa": r["_id"],
            "txn_count_last_1hr": r["count"],
            "total_amount": r["total_amount"]
        }
        for r in results
    ]


def get_graph_risk_signals():
    return list(
        graph_col
        .find({"count": {"$gte": 4}}, {"_id": 0})
        .sort("count", -1)
        .limit(20)
    )
