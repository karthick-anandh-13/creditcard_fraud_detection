import joblib
import pandas as pd
from pathlib import Path
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split

# =====================================================
# PATH SETUP
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

# =====================================================
# LOAD UPI DATASET
# =====================================================
DATA_FILE = DATA_DIR / "upi_fraud_data.csv"

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"UPI dataset not found at {DATA_FILE}. "
        "Generate synthetic UPI data first."
    )

df = pd.read_csv(DATA_FILE)

if "is_fraud" not in df.columns:
    raise ValueError("Dataset must contain 'is_fraud' column")

X = df.drop(columns=["is_fraud"])
y = df["is_fraud"]

# =====================================================
# TRAIN / VALIDATION SPLIT
# =====================================================
X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# =====================================================
# LOAD BASE LIGHTGBM MODEL
# =====================================================
BASE_MODEL_PATH = MODEL_DIR / "upi_fraud_lgbm.pkl"

if not BASE_MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Base UPI LightGBM model not found at {BASE_MODEL_PATH}"
    )

base_model = joblib.load(BASE_MODEL_PATH)

# =====================================================
# CALIBRATION (SIGMOID)
# =====================================================
calibrated_model = CalibratedClassifierCV(
    estimator=base_model,
    method="sigmoid",
    cv="prefit"
)

calibrated_model.fit(X_val, y_val)

# =====================================================
# SAVE CALIBRATED MODEL
# =====================================================
CALIBRATED_MODEL_PATH = MODEL_DIR / "upi_fraud_lgbm_calibrated.pkl"

joblib.dump(calibrated_model, CALIBRATED_MODEL_PATH)

print("✅ UPI calibrated LightGBM model saved successfully")
print(f"📦 Path: {CALIBRATED_MODEL_PATH}")
