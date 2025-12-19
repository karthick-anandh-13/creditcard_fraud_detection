from datetime import datetime, timedelta
from storage.mongo import db

class VelocityStore:
    def __init__(self):
        self.col = db["upi_velocity"]

    def record_transaction(self, payer_vpa: str, amount: float, timestamp: datetime):
        self.col.insert_one({
            "payer_vpa": payer_vpa,
            "amount": amount,
            "timestamp": timestamp
        })

    def get_features(self, payer_vpa: str, now: datetime) -> dict:
        last_1hr = now - timedelta(hours=1)
        last_24hr = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        txns = list(self.col.find({
            "payer_vpa": payer_vpa,
            "timestamp": {"$gte": last_7d}
        }))

        tx_1hr = [t for t in txns if t["timestamp"] >= last_1hr]
        tx_24hr = [t for t in txns if t["timestamp"] >= last_24hr]

        avg_7d = (
            sum(t["amount"] for t in txns) / len(txns)
            if txns else 0.0
        )

        return {
            "transactions_last_1hr": len(tx_1hr),
            "transactions_last_24hr": len(tx_24hr),
            "avg_amount_last_7_days": avg_7d
        }
