# state/risk_profile_store.py

from datetime import datetime
from storage.mongo import db


class RiskProfileStore:
    def __init__(self):
        self.col = db["risk_profiles"]
        self.col.create_index("payer_vpa", unique=True)

    # --------------------------------------------------
    # DEFAULT PROFILE
    # --------------------------------------------------
    def _default_profile(self, payer_vpa: str):
        return {
            "payer_vpa": payer_vpa,
            "risk_score": 20,
            "block_threshold": 0.85,
            "step_up_threshold": 0.35,
            "allow_count": 0,
            "block_count": 0,
            "stepup_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    # --------------------------------------------------
    # GET CURRENT THRESHOLDS
    # --------------------------------------------------
    def get_thresholds(self, payer_vpa: str):
        profile = self.col.find_one(
            {"payer_vpa": payer_vpa},
            {"block_threshold": 1, "step_up_threshold": 1}
        )

        if not profile:
            profile = self._default_profile(payer_vpa)
            self.col.insert_one(profile)

        return {
            "BLOCK": profile["block_threshold"],
            "STEP_UP": profile["step_up_threshold"]
        }

    # --------------------------------------------------
    # UPDATE RISK PROFILE (ATOMIC)
    # --------------------------------------------------
    def update(self, payer_vpa: str, decision: str):
        profile = self.col.find_one({"payer_vpa": payer_vpa})

        if not profile:
            profile = self._default_profile(payer_vpa)
            self.col.insert_one(profile)

        risk_score = profile["risk_score"]

        allow_count = profile["allow_count"]
        block_count = profile["block_count"]
        stepup_count = profile["stepup_count"]

        # ---------------------------
        # Adaptive learning
        # ---------------------------
        if decision == "BLOCK":
            risk_score = min(100, risk_score + 15)
            block_count += 1

        elif decision == "STEP_UP_AUTH":
            risk_score = min(100, risk_score + 5)
            stepup_count += 1

        else:  # ALLOW
            risk_score = max(0, risk_score - 2)
            allow_count += 1

        # ---------------------------
        # Dynamic thresholds
        # ---------------------------
        block_threshold = max(0.60, 0.85 - (risk_score / 300))
        step_up_threshold = max(0.20, 0.35 - (risk_score / 500))

        # ---------------------------
        # Atomic update
        # ---------------------------
        self.col.update_one(
            {"payer_vpa": payer_vpa},
            {
                "$set": {
                    "risk_score": risk_score,
                    "block_threshold": round(block_threshold, 4),
                    "step_up_threshold": round(step_up_threshold, 4),
                    "updated_at": datetime.utcnow()
                },
                "$inc": {
                    "allow_count": allow_count - profile["allow_count"],
                    "block_count": block_count - profile["block_count"],
                    "stepup_count": stepup_count - profile["stepup_count"]
                }
            }
        )
