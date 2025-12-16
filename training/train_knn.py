import pandas as pd
import joblib
from pathlib import Path
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from data.schema import FEATURE_COLUMNS

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "creditcard.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

# Load data
df = pd.read_csv(DATA_PATH)

# Use only normal transactions
df_normal = df[df["Class"] == 0]

X = df_normal[FEATURE_COLUMNS]

# Scale features (important for KNN)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train KNN (Nearest Neighbors)
knn = NearestNeighbors(
    n_neighbors=5,
    metric="euclidean",
    n_jobs=-1
)

knn.fit(X_scaled)

# Save model + scaler
joblib.dump(
    {"model": knn, "scaler": scaler},
    MODEL_DIR / "fraud_knn.pkl"
)

print("KNN anomaly model trained and saved")
