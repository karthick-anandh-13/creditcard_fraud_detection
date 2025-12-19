# storage/risk_profile_repo.py

from datetime import datetime
from storage.mongo import db


class RiskProfileStore:
    """
    Stores adaptive risk profiles and thresholds per UPI payer.
    Backed by MongoDB.
    """

    def __init__(self):
        self.collection = db["upi_risk_profiles"]

    # --------------------------------------------------
    # DEFAULT PROFILE
    # --------------------------------------------------
    def _default_profile(self, payer_vpa: str) -> dict:
        return {
            "payer_vpa": payer_vpa,
            "risk_score": 20,                 # 0–100
            "block_threshold": 0.85,
            "step_up_threshold": 0.45,
            "allow_count": 0,
            "block_count": 0,
            "stepup_count": 0,
            "last_updated": datetime.utcnow()
        }

    # --------------------------------------------------
    # READ THRESHOLDS (used by fraud consumer)
    # --------------------------------------------------
    def get_thresholds(self, payer_vpa: str) -> dict:
        doc = self.collection.find_one({"payer_vpa": payer_vpa})

        if not doc:
            doc = self._default_profile(payer_vpa)
            self.collection.insert_one(doc)

        return {
            "BLOCK": doc["block_threshold"],
            "STEP_UP": doc["step_up_threshold"]
        }

    # --------------------------------------------------
    # UPDATE FROM REAL-TIME DECISIONS
    # --------------------------------------------------
    def update(self, payer_vpa: str, decision: str):
        doc = self.collection.find_one({"payer_vpa": payer_vpa})

        if not doc:
            doc = self._default_profile(payer_vpa)

        risk_score = doc["risk_score"]

        # -------------------------
        # Adaptive learning
        # -------------------------
        if decision == "BLOCK":
            risk_score = min(100, risk_score + 15)
            doc["block_count"] += 1

        elif decision == "STEP_UP_AUTH":
            risk_score = min(100, risk_score + 5)
            doc["stepup_count"] += 1

        elif decision == "ALLOW":
            risk_score = max(0, risk_score - 2)
            doc["allow_count"] += 1

        # -------------------------
        # Dynamic thresholds derived from risk
        # -------------------------
        block_threshold = max(0.60, 0.85 - (risk_score / 300))
        step_up_threshold = max(0.25, 0.45 - (risk_score / 500))

        # -------------------------
        # Persist
        # -------------------------
        self.collection.update_one(
            {"payer_vpa": payer_vpa},
            {"$set": {
                "risk_score": risk_score,
                "block_threshold": block_threshold,
                "step_up_threshold": step_up_threshold,
                "allow_count": doc["allow_count"],
                "block_count": doc["block_count"],
                "stepup_count": doc["stepup_count"],
                "last_updated": datetime.utcnow()
            }},
            upsert=True
        )

    # --------------------------------------------------
    # ONLINE LEARNING FROM FEEDBACK
    # --------------------------------------------------
    def tighten_user_thresholds(self, payer_vpa: str):
        """
        Called when fraud slipped through (false negative).
        """
        self.collection.update_one(
            {"payer_vpa": payer_vpa},
            {"$inc": {"risk_score": 10}},
            upsert=True
        )
        print(f"[USER LEARNING] tightened thresholds for {payer_vpa}")

    def relax_user_thresholds(self, payer_vpa: str):
        """
        Called when customer was wrongly blocked (false positive).
        """
        self.collection.update_one(
            {"payer_vpa": payer_vpa},
            {"$inc": {"risk_score": -5}},
            upsert=True
        )
        print(f"[USER LEARNING] relaxed thresholds for {payer_vpa}")
