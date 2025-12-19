from fastapi import APIRouter
from storage.mongo import db

router = APIRouter()

@router.get("/user/{payer_vpa}")
def get_user_risk(payer_vpa: str):
    profile = db["upi_risk_profiles"].find_one(
        {"payer_vpa": payer_vpa},
        {"_id": 0}
    )

    if not profile:
        return {"message": "No risk profile found"}

    return profile
