from fastapi import APIRouter
from storage.mongo import db

router = APIRouter()

@router.get("/recent")
def recent_transactions(limit: int = 20):
    logs = (
        db["decision_logs"]
        .find({}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )

    return list(logs)
