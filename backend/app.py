from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path
import os
from dotenv import load_dotenv
import logging
import shap

from data.schema import FEATURE_COLUMNS
from data.upi_schema import UPI_FEATURE_COLUMNS

# =====================================================
# ENV + LOGGING
# =====================================================
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# =====================================================
# FASTAPI APP
# =====================================================
app = FastAPI(
    title="Transaction Fraud Detection API",
    version="1.0.0"
)

# =====================================================
# PATHS
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

# =====================================================
# RISK SCORING FUNCTION (FIXED: WAS MISSING)
# =====================================================
def risk_score(prob: float):
    if prob >= 0.85:
        return 90, "CRITICAL"
    elif prob >= 0.65:
        return 75, "HIGH"
    elif prob >= 0.35:
        return 50, "MEDIUM"
    else:
        return 20, "LOW"

# =====================================================
# LOAD CREDIT CARD MODELS
# =====================================================
MODELS = {}

try:
    MODELS["lightgbm"] = joblib.load(MODEL_DIR / "fraud_lgbm.pkl")
    MODELS["xgboost"] = joblib.load(MODEL_DIR / "fraud_xgb.pkl")
    logger.info("LightGBM and XGBoost loaded")
except Exception as e:
    logger.exception("Failed to load main models")
    raise RuntimeError(str(e))

try:
    MODELS["decision_tree"] = joblib.load(MODEL_DIR / "fraud_decision_tree.pkl")
    logger.info("Decision Tree loaded")
except Exception:
    logger.warning("Decision Tree not available")

# =====================================================
# LOAD ANOMALY MODELS
# =====================================================
ISO_MODEL = None
KNN_MODEL = None
KNN_SCALER = None

try:
    ISO_MODEL = joblib.load(MODEL_DIR / "fraud_isolation_forest.pkl")
    logger.info("Isolation Forest loaded")
except Exception:
    logger.warning("Isolation Forest not available")

try:
    knn_bundle = joblib.load(MODEL_DIR / "fraud_knn.pkl")
    KNN_MODEL = knn_bundle["model"]
    KNN_SCALER = knn_bundle["scaler"]
    logger.info("KNN anomaly model loaded")
except Exception:
    logger.warning("KNN model not available")

# =====================================================
# SHAP (CREDIT CARD – LIGHTGBM)
# =====================================================
SHAP_EXPLAINER = None
try:
    lgbm_pipeline = MODELS["lightgbm"]
    lgbm_model = lgbm_pipeline.steps[-1][1]
    SHAP_EXPLAINER = shap.TreeExplainer(lgbm_model)
    logger.info("SHAP explainer initialized (credit card)")
except Exception:
    logger.warning("SHAP explainer not available")

# =====================================================
# LOAD UPI MODELS
# =====================================================
UPI_MODELS = {}

try:
    UPI_MODELS["lightgbm"] = joblib.load(MODEL_DIR / "upi_fraud_lgbm.pkl")
    logger.info("UPI LightGBM model loaded")
except Exception:
    logger.warning("UPI LightGBM model not available")

try:
    UPI_MODELS["lightgbm_calibrated"] = joblib.load(
        MODEL_DIR / "upi_fraud_lgbm_calibrated.pkl"
    )
    logger.info("UPI calibrated model loaded")
except Exception:
    logger.warning("UPI calibrated model not available")

# =====================================================
# SHAP (UPI – LIGHTGBM)
# =====================================================
UPI_SHAP_EXPLAINER = None
try:
    if "lightgbm" in UPI_MODELS:
        UPI_SHAP_EXPLAINER = shap.TreeExplainer(UPI_MODELS["lightgbm"])
        logger.info("UPI SHAP explainer initialized")
except Exception:
    logger.warning("UPI SHAP explainer not available")

# =====================================================
# REQUEST SCHEMAS
# =====================================================
class Transaction(BaseModel):
    Time: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float


class UPITransaction(BaseModel):
    transaction_amount: float
    hour_of_day: int
    day_of_week: int
    transactions_last_1hr: int
    transactions_last_24hr: int
    avg_amount_last_7_days: float
    device_change_flag: int
    location_change_flag: int
    failed_attempts_last_1hr: int
    receiver_new_flag: int

# =====================================================
# CREDIT CARD PREDICTION
# =====================================================
@app.post("/predict")
def predict(transaction: Transaction,
            model_name: str = Query("lightgbm", enum=["lightgbm", "xgboost", "decision_tree"])):

    pipeline = MODELS[model_name]
    X = pd.DataFrame([[getattr(transaction, c) for c in FEATURE_COLUMNS]],
                     columns=FEATURE_COLUMNS)

    prob = pipeline.predict_proba(X)[0][1]
    threshold = float(os.getenv("FRAUD_THRESHOLD", 0.5))

    return {
        "model": model_name,
        "fraud_probability": float(prob),
        "is_fraud": bool(prob >= threshold)
    }

# =====================================================
# HYBRID CREDIT CARD PREDICTION
# =====================================================
@app.post("/predict/hybrid")
def predict_hybrid(transaction: Transaction,
                   model_name: str = Query("lightgbm", enum=["lightgbm", "xgboost", "decision_tree"])):

    pipeline = MODELS[model_name]
    X = pd.DataFrame([[getattr(transaction, c) for c in FEATURE_COLUMNS]],
                     columns=FEATURE_COLUMNS)

    prob = pipeline.predict_proba(X)[0][1]

    iso_anomaly = ISO_MODEL is not None and ISO_MODEL.predict(X)[0] == -1

    knn_anomaly = False
    if KNN_MODEL is not None:
        X_scaled = KNN_SCALER.transform(X)
        knn_anomaly = X_scaled.mean() > 3.0

    threshold = float(os.getenv("FRAUD_THRESHOLD", 0.5))

    return {
        "fraud_probability": float(prob),
        "isolation_forest_anomaly": iso_anomaly,
        "knn_anomaly": knn_anomaly,
        "final_decision": bool(prob >= threshold or iso_anomaly or knn_anomaly)
    }

# =====================================================
# UPI RISK PREDICTION (CALIBRATED)
# =====================================================
@app.post("/upi/predict/risk")
def predict_upi_risk(transaction: UPITransaction):
    if "lightgbm_calibrated" not in UPI_MODELS:
        raise HTTPException(500, "Calibrated model not available")

    model = UPI_MODELS["lightgbm_calibrated"]
    X = pd.DataFrame([transaction.dict()])

    prob = model.predict_proba(X)[0][1]
    score, level = risk_score(prob)

    return {
        "domain": "upi",
        "calibrated_probability": float(prob),
        "risk_score": score,
        "risk_level": level,
        "recommended_action": (
            "BLOCK" if level == "CRITICAL"
            else "STEP_UP_AUTH" if level in ["HIGH", "MEDIUM"]
            else "ALLOW"
        )
    }

# =====================================================
# HEALTH
# =====================================================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "credit_models": list(MODELS.keys()),
        "upi_models": list(UPI_MODELS.keys())
    }
