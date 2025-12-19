from datetime import datetime, timedelta
from storage.mongo_client import velocity_col

class VelocityStore:
    def record_transaction(self, payer_vpa, amount, timestamp):
        velocity_col.insert_one({
            "payer_vpa": payer_vpa,
            "amount": amount,
            "timestamp": timestamp
        })

    def get_features(self, payer_vpa, now):
        one_hr = now - timedelta(hours=1)
        one_day = now - timedelta(days=1)
        seven_days = now - timedelta(days=7)

        txns_1hr = velocity_col.count_documents({
            "payer_vpa": payer_vpa,
            "timestamp": {"$gte": one_hr}
        })

        txns_24hr = velocity_col.count_documents({
            "payer_vpa": payer_vpa,
            "timestamp": {"$gte": one_day}
        })

        amounts_7d = list(
            velocity_col.find(
                {
                    "payer_vpa": payer_vpa,
                    "timestamp": {"$gte": seven_days}
                },
                {"amount": 1, "_id": 0}
            )
        )

        avg_7d = (
            sum(a["amount"] for a in amounts_7d) / len(amounts_7d)
            if amounts_7d else 0.0
        )

        return {
            "transactions_last_1hr": txns_1hr,
            "transactions_last_24hr": txns_24hr,
            "avg_amount_last_7_days": avg_7d
        }
