from pydantic import BaseModel
from datetime import datetime


class FraudDecision(BaseModel):
    transaction_id: str
    payer_vpa: str
    payee_vpa: str
    amount: float
    decision: str
    final_probability: float | None
    graph_override: str | None
    timestamp: datetime


class RiskSummary(BaseModel):
    total_transactions: int
    blocked: int
    step_up: int
    allowed: int
