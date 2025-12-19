# state/decision_explainer.py

def explain_decision(
    ml_prob: float,
    velocity: dict,
    velocity_risk: float,
    graph_signals: dict,
    final_decision: str
) -> list[str]:
    """
    Converts model + behavioral signals into
    human-readable explanations (bank-grade).
    """

    explanations = []

    # ===============================
    # ML EXPLANATION
    # ===============================
    if ml_prob >= 0.8:
        explanations.append(f"High ML fraud probability ({ml_prob:.2f})")
    elif ml_prob >= 0.6:
        explanations.append(f"Moderate ML fraud probability ({ml_prob:.2f})")

    # ===============================
    # VELOCITY EXPLANATIONS
    # ===============================
    if velocity.get("transactions_last_1hr", 0) >= 5:
        explanations.append(
            f"{velocity['transactions_last_1hr']} transactions in last 1 hour"
        )

    if velocity.get("transactions_last_24hr", 0) >= 20:
        explanations.append(
            f"{velocity['transactions_last_24hr']} transactions in last 24 hours"
        )

    if velocity.get("avg_amount_last_7_days", 0) > 0:
        ratio = velocity_risk
        if ratio >= 0.3:
            explanations.append("Transaction amount significantly higher than normal")

    # ===============================
    # GRAPH EXPLANATIONS
    # ===============================
    if graph_signals.get("payer_unique_payees", 0) >= 6:
        explanations.append(
            f"Payer connected to {graph_signals['payer_unique_payees']} unique payees"
        )

    if graph_signals.get("payee_unique_payers", 0) >= 20:
        explanations.append(
            f"Payee receiving money from many unique payers ({graph_signals['payee_unique_payers']})"
        )

    if graph_signals.get("edge_count", 0) >= 4:
        explanations.append("Repeated transactions to same payee detected")

    # ===============================
    # FALLBACK
    # ===============================
    if not explanations:
        explanations.append("Transaction behavior within normal limits")

    return explanations
