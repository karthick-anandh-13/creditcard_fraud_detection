import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest

from data.schema import FEATURE_COLUMNS

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "creditcard.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

# Load data
df = pd.read_csv(DATA_PATH)

# Use ONLY normal transactions for training
df_normal = df[df["Class"] == 0]

X = df_normal[FEATURE_COLUMNS]

# Train Isolation Forest
iso_forest = IsolationForest(
    n_estimators=200,
    contamination=0.002,   # fraud rate ~0.17%
    random_state=42,
    n_jobs=-1
)

iso_forest.fit(X)

# Save model
joblib.dump(iso_forest, MODEL_DIR / "fraud_isolation_forest.pkl")

print("Isolation Forest model trained and saved")
