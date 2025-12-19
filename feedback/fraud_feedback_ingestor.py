import json
from pathlib import Path
from datetime import datetime

# =====================================================
# PATH SETUP
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
FEEDBACK_DIR = BASE_DIR / "feedback" / "data"
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

FEEDBACK_FILE = FEEDBACK_DIR / "fraud_feedback.log"

# =====================================================
# FEEDBACK INGESTOR
# =====================================================
def record_fraud_feedback(
    transaction_id: str,
    payer_vpa: str,
    payee_vpa: str,
    final_decision: str,
    actual_outcome: str,
    source: str
):
    """
    Stores confirmed fraud / genuine outcomes
    Used for drift detection, retraining, audits
    """

    feedback = {
        "transaction_id": transaction_id,
        "payer_vpa": payer_vpa,
        "payee_vpa": payee_vpa,
        "final_decision": final_decision,
        "actual_outcome": actual_outcome,  # FRAUD | GENUINE
        "source": source,
        "reported_at": datetime.utcnow().isoformat()
    }

    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback) + "\n")

    print(
        f"[FEEDBACK] txn={transaction_id} | outcome={actual_outcome}"
    )


# =====================================================
# MANUAL TEST (ONLY RUNS WHEN EXECUTED DIRECTLY)
# =====================================================
if __name__ == "__main__":
    record_fraud_feedback(
        transaction_id="abc-123",
        payer_vpa="user@upi",
        payee_vpa="merchant@upi",
        final_decision="ALLOW",
        actual_outcome="FRAUD",
        source="CUSTOMER_COMPLAINT"
    )
