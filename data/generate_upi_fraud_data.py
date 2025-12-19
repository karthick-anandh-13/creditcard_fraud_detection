import random
import pandas as pd
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================
N_SAMPLES = 20000
FRAUD_RATIO = 0.08   # 8% fraud (realistic for UPI)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = DATA_DIR / "upi_fraud_data.csv"

# =====================================================
# DATA GENERATION
# =====================================================
records = []

for _ in range(N_SAMPLES):
    is_fraud = 1 if random.random() < FRAUD_RATIO else 0

    transaction_amount = (
        random.uniform(2000, 10000) if is_fraud
        else random.uniform(10, 3000)
    )

    hour_of_day = random.randint(0, 23)
    day_of_week = random.randint(0, 6)

    transactions_last_1hr = (
        random.randint(5, 20) if is_fraud else random.randint(0, 3)
    )

    transactions_last_24hr = (
        random.randint(20, 80) if is_fraud else random.randint(1, 10)
    )

    avg_amount_last_7_days = (
        transaction_amount * random.uniform(0.8, 1.2)
    )

    device_change_flag = 1 if is_fraud and random.random() < 0.4 else 0
    location_change_flag = 1 if is_fraud and random.random() < 0.3 else 0
    failed_attempts_last_1hr = (
        random.randint(1, 5) if is_fraud else 0
    )

    receiver_new_flag = 1 if is_fraud and random.random() < 0.5 else 0

    records.append({
        "transaction_amount": round(transaction_amount, 2),
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "transactions_last_1hr": transactions_last_1hr,
        "transactions_last_24hr": transactions_last_24hr,
        "avg_amount_last_7_days": round(avg_amount_last_7_days, 2),
        "device_change_flag": device_change_flag,
        "location_change_flag": location_change_flag,
        "failed_attempts_last_1hr": failed_attempts_last_1hr,
        "receiver_new_flag": receiver_new_flag,
        "is_fraud": is_fraud
    })

# =====================================================
# SAVE
# =====================================================
df = pd.DataFrame(records)
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Synthetic UPI fraud dataset generated: {OUTPUT_FILE}")
print(df["is_fraud"].value_counts(normalize=True))
