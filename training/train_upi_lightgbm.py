import joblib
import pandas as pd
from pathlib import Path
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# =====================================================
# PATHS
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

DATA_FILE = DATA_DIR / "upi_fraud_data.csv"

# =====================================================
# LOAD DATA
# =====================================================
if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

df = pd.read_csv(DATA_FILE)

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
# LIGHTGBM MODEL
# =====================================================
model = LGBMClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=-1,
    num_leaves=64,
    subsample=0.8,
    colsample_bytree=0.8,
    class_weight="balanced",
    random_state=42
)

# =====================================================
# TRAIN
# =====================================================
model.fit(X_train, y_train)

# =====================================================
# EVALUATION
# =====================================================
val_probs = model.predict_proba(X_val)[:, 1]
val_preds = (val_probs >= 0.5).astype(int)

print("\n=== Classification Report ===")
print(classification_report(y_val, val_preds))

print("ROC-AUC:", roc_auc_score(y_val, val_probs))

# =====================================================
# SAVE MODEL
# =====================================================
MODEL_PATH = MODEL_DIR / "upi_fraud_lgbm.pkl"
joblib.dump(model, MODEL_PATH)

print(f"\n✅ Base UPI LightGBM model saved at: {MODEL_PATH}")
