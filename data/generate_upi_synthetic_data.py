import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

# -------------------------------------------------
# Configuration
# -------------------------------------------------
N_SAMPLES = 20000
FRAUD_RATIO = 0.05  # 5% fraud

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "data" / "raw" / "upi_transactions.csv"

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def generate_legit_transaction():
    return {
        "transaction_amount": np.random.uniform(10, 3000),
        "hour_of_day": np.random.randint(6, 23),
        "day_of_week": np.random.randint(0, 7),
        "transactions_last_1hr": np.random.randint(0, 3),
        "transactions_last_24hr": np.random.randint(1, 10),
        "avg_amount_last_7_days": np.random.uniform(50, 2500),
        "device_change_flag": 0,
        "location_change_flag": 0,
        "failed_attempts_last_1hr": np.random.randint(0, 1),
        "receiver_new_flag": 0,
        "is_fraud": 0
    }

def generate_fraud_transaction():
    return {
        "transaction_amount": np.random.uniform(3000, 50000),
        "hour_of_day": np.random.choice([0, 1, 2, 3, 23]),
        "day_of_week": np.random.randint(0, 7),
        "transactions_last_1hr": np.random.randint(5, 20),
        "transactions_last_24hr": np.random.randint(10, 50),
        "avg_amount_last_7_days": np.random.uniform(500, 5000),
        "device_change_flag": 1,
        "location_change_flag": 1,
        "failed_attempts_last_1hr": np.random.randint(2, 6),
        "receiver_new_flag": 1,
        "is_fraud": 1
    }

# -------------------------------------------------
# Generate dataset
# -------------------------------------------------
rows = []

n_fraud = int(N_SAMPLES * FRAUD_RATIO)
n_legit = N_SAMPLES - n_fraud

for _ in range(n_legit):
    rows.append(generate_legit_transaction())

for _ in range(n_fraud):
    rows.append(generate_fraud_transaction())

df = pd.DataFrame(rows)

# Shuffle dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# SaveS
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print(f"UPI synthetic dataset generated at: {OUTPUT_PATH}")
print(df["is_fraud"].value_counts())
