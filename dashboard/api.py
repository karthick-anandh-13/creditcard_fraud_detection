from fastapi import FastAPI
from dashboard.services import (
    get_recent_decisions,
    get_risk_summary,
    get_top_risky_users,
    get_velocity_alerts,
    get_graph_risk_signals
)

app = FastAPI(
    title="UPI Fraud Ops Dashboard",
    version="1.0"
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/decisions/recent")
def recent_decisions(limit: int = 50):
    return get_recent_decisions(limit)

@app.get("/summary")
def summary():
    return get_risk_summary()

@app.get("/users/top-risky")
def top_risky_users(limit: int = 10):
    return get_top_risky_users(limit)

@app.get("/alerts/velocity")
def velocity_alerts():
    return get_velocity_alerts()

@app.get("/alerts/graph")
def graph_alerts():
    return get_graph_risk_signals()
