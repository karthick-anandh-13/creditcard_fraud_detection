import random
from datetime import datetime
from uuid import uuid4

from events.upi_event import UPITransactionEvent
from event_queue.event_queue import push_event


def generate_upi_event():
    return UPITransactionEvent(
        transaction_id=str(uuid4()),
        payer_vpa=f"user{random.randint(1,1000)}@upi",
        payee_vpa=f"merchant{random.randint(1,200)}@upi",
        amount=round(random.uniform(10, 5000), 2),
        timestamp=datetime.utcnow(),
        device_id=f"device_{random.randint(1,300)}",
        ip_address=f"192.168.1.{random.randint(1,255)}",
        bank_code=random.choice(["HDFC", "ICICI", "SBI", "AXIS"])
    )


if __name__ == "__main__":
    event = generate_upi_event()
    push_event(event.model_dump())
    print("Event pushed to queue")
