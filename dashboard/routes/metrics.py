from fastapi import APIRouter
from storage.mongo import db

router = APIRouter()

@router.get("/summary")
def system_metrics():
    col = db["decision_logs"]

    total = col.count_documents({})
    blocked = col.count_documents({"decision": "BLOCK"})
    step_up = col.count_documents({"decision": "STEP_UP_AUTH"})
    allowed = col.count_documents({"decision": "ALLOW"})

    return {
        "total_transactions": total,
        "blocked": blocked,
        "step_up": step_up,
        "allowed": allowed,
        "block_rate": round(blocked / total, 4) if total else 0
    }
