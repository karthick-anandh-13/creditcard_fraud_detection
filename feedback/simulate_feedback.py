from feedback.fraud_feedback_ingestor import record_fraud_feedback
import random

DECISIONS = ["ALLOW", "BLOCK"]
OUTCOMES = ["FRAUD", "GENUINE"]

for i in range(30):
    record_fraud_feedback(
        transaction_id=f"sim-{i}",
        payer_vpa=f"user{i}@upi",
        payee_vpa=f"merchant{i}@upi",
        final_decision=random.choices(
            DECISIONS, weights=[0.7, 0.3]
        )[0],
        actual_outcome=random.choices(
            OUTCOMES, weights=[0.4, 0.6]
        )[0],
        source="BANK_REVIEW"
    )

print("✅ Synthetic feedback generated")
