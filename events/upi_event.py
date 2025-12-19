from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4


class UPITransactionEvent(BaseModel):
    event_id: str = str(uuid4())
    transaction_id: str
    payer_vpa: str
    payee_vpa: str
    amount: float
    timestamp: datetime
    device_id: str
    ip_address: str
    bank_code: str
    status: str = "INITIATED"
