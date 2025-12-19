from event_queue.event_queue import read_events, clear_queue
from audit.decision_log import log_decision

from storage.velocity_repo import VelocityStore
from storage.risk_profile_repo import RiskProfileStore
from storage.graph_repo import GraphStore
from storage.processed_txn_store import ProcessedTransactionStore

from state.decision_explainer import explain_decision

import joblib
from pathlib import Path
import pandas as pd

# =====================================================
# GLOBAL STORES (STATEFUL)
# =====================================================
velocity_store = VelocityStore()
risk_store = RiskProfileStore()
graph_store = GraphStore()
processed_store = ProcessedTransactionStore()

# =====================================================
# LOAD MODELS (CHAMPION + CHALLENGER)
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

# 🎯 Champion (ACTIVE)
CHAMPION_MODEL = joblib.load(
    MODEL_DIR / "upi_fraud_lgbm_calibrated.pkl"
)

# 🧪 Challenger (SHADOW – no decisions)
CHALLENGER_MODEL = joblib.load(
    MODEL_DIR / "upi_fraud_lgbm.pkl"
)

# =====================================================
# FEATURE EXTRACTION
# =====================================================
def extract_upi_features(event: dict) -> tuple[pd.DataFrame, dict]:
    now = pd.to_datetime(event["timestamp"])

    velocity = velocity_store.get_features(
        payer_vpa=event["payer_vpa"],
        now=now
    )

    X = pd.DataFrame([{
        "transaction_amount": event["amount"],
        "hour_of_day": now.hour,
        "day_of_week": now.weekday(),
        "transactions_last_1hr": velocity["transactions_last_1hr"],
        "transactions_last_24hr": velocity["transactions_last_24hr"],
        "avg_amount_last_7_days": velocity["avg_amount_last_7_days"],
        "device_change_flag": 0,
        "location_change_flag": 0,
        "failed_attempts_last_1hr": 0,
        "receiver_new_flag": 0
    }])

    return X, velocity

# =====================================================
# VELOCITY RISK
# =====================================================
def compute_velocity_risk(event: dict, velocity: dict) -> float:
    risk = 0.0

    if velocity["transactions_last_1hr"] >= 5:
        risk += 0.2
    if velocity["transactions_last_24hr"] >= 20:
        risk += 0.3
    if velocity["avg_amount_last_7_days"] > 0:
        if event["amount"] / velocity["avg_amount_last_7_days"] >= 3:
            risk += 0.3

    return risk

# =====================================================
# MAIN CONSUMER LOOP
# =====================================================
def consume_events():
    events = read_events()

    if not events:
        print("No events to process")
        return

    for event in events:
        txn_id = event["transaction_id"]

        # 🔐 Idempotency
        if processed_store.is_processed(txn_id):
            print(f"[SKIP] Duplicate txn ignored | {txn_id}")
            continue

        # 1️⃣ Feature extraction
        X, velocity = extract_upi_features(event)

        # 2️⃣ MODEL SCORING
        champion_prob = CHAMPION_MODEL.predict_proba(X)[0][1]
        challenger_prob = CHALLENGER_MODEL.predict_proba(X)[0][1]

        # 3️⃣ Velocity risk
        velocity_risk = compute_velocity_risk(event, velocity)

        # 4️⃣ Final probability (Champion only)
        final_prob = min(1.0, champion_prob + velocity_risk)

        # =================================================
        # GRAPH INTELLIGENCE
        # =================================================
        graph_store.record_transaction(
            payer_vpa=event["payer_vpa"],
            payee_vpa=event["payee_vpa"],
            amount=event["amount"],
            timestamp=pd.to_datetime(event["timestamp"])
        )

        payer_unique_payees = graph_store.get_unique_payees(event["payer_vpa"])
        payee_unique_payers = graph_store.get_unique_payers(event["payee_vpa"])
        edge_stats = graph_store.get_edge_stats(
            event["payer_vpa"], event["payee_vpa"]
        )
        edge_count = edge_stats["count"] if edge_stats else 0

        graph_override = None
        if payer_unique_payees >= 6:
            graph_override = "PAYER_MULE_PATTERN"
        elif payee_unique_payers >= 20:
            graph_override = "SCAM_MERCHANT_PATTERN"
        elif edge_count >= 4:
            graph_override = "REPEATED_EDGE_ABUSE"

        # =================================================
        # DECISION ENGINE (CHAMPION ONLY)
        # =================================================
        thresholds = risk_store.get_thresholds(event["payer_vpa"])

        if graph_override:
            decision = "BLOCK"
        elif final_prob >= thresholds["BLOCK"]:
            decision = "BLOCK"
        elif final_prob >= thresholds["STEP_UP"]:
            decision = "STEP_UP_AUTH"
        else:
            decision = "ALLOW"

        # 🧠 Explainability
        explanations = explain_decision(
            ml_prob=champion_prob,
            velocity=velocity,
            velocity_risk=velocity_risk,
            graph_signals={
                "payer_unique_payees": payer_unique_payees,
                "payee_unique_payers": payee_unique_payers,
                "edge_count": edge_count
            },
            final_decision=decision
        )

        # Update risk profile
        risk_store.update(event["payer_vpa"], decision)

        # =================================================
        # AUDIT LOG (Champion vs Challenger)
        # =================================================
        log_decision({
            "transaction_id": txn_id,
            "payer_vpa": event["payer_vpa"],
            "payee_vpa": event["payee_vpa"],
            "amount": event["amount"],
            "champion_probability": round(champion_prob, 6),
            "challenger_probability": round(challenger_prob, 6),
            "velocity_risk": round(velocity_risk, 3),
            "final_probability": round(final_prob, 6),
            "graph_override": graph_override,
            "decision": decision,
            "explanations": explanations
        })

        processed_store.mark_processed(txn_id, decision)

        print(
            f"[UPI] txn={txn_id} | decision={decision} | "
            f"champion={champion_prob:.3f} | challenger={challenger_prob:.3f}"
        )

        velocity_store.record_transaction(
            payer_vpa=event["payer_vpa"],
            amount=event["amount"],
            timestamp=pd.to_datetime(event["timestamp"])
        )

    clear_queue()
    print("Queue cleared")

# =====================================================
# ENTRY POINT
# =====================================================
if __name__ == "__main__":
    consume_events()
