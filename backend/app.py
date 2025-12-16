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
    title="Credit Card Fraud Detection API",
    version="1.0.0"
)

# =====================================================
# PATHS
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

# =====================================================
# LOAD SUPERVISED MODELS
# =====================================================
MODELS = {}

try:
    MODELS["lightgbm"] = joblib.load(MODEL_DIR / "fraud_lgbm.pkl")
    MODELS["xgboost"] = joblib.load(MODEL_DIR / "fraud_xgb.pkl")
    logger.info("LightGBM and XGBoost loaded")
except Exception as e:
    logger.exception("Failed to load main models")
    raise RuntimeError(str(e))

# Decision Tree
try:
    MODELS["decision_tree"] = joblib.load(MODEL_DIR / "fraud_decision_tree.pkl")
    logger.info("Decision Tree loaded")
except Exception:
    logger.warning("Decision Tree not available")

# =====================================================
# LOAD ISOLATION FOREST
# =====================================================
ISO_MODEL = None
try:
    ISO_MODEL = joblib.load(MODEL_DIR / "fraud_isolation_forest.pkl")
    logger.info("Isolation Forest loaded")
except Exception:
    logger.warning("Isolation Forest not available")

# =====================================================
# LOAD KNN ANOMALY MODEL
# =====================================================
KNN_MODEL = None
KNN_SCALER = None

try:
    knn_bundle = joblib.load(MODEL_DIR / "fraud_knn.pkl")
    KNN_MODEL = knn_bundle["model"]
    KNN_SCALER = knn_bundle["scaler"]
    logger.info("KNN anomaly model loaded")
except Exception:
    logger.warning("KNN model not available")

# =====================================================
# SHAP (LIGHTGBM ONLY)
# =====================================================
SHAP_EXPLAINER = None
try:
    lgbm_pipeline = MODELS["lightgbm"]
    lgbm_model = lgbm_pipeline.steps[-1][1]
    SHAP_EXPLAINER = shap.TreeExplainer(lgbm_model)
    logger.info("SHAP explainer initialized")
except Exception:
    logger.warning("SHAP explainer not available")

# =====================================================
# REQUEST SCHEMA
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

# =====================================================
# SINGLE PREDICTION
# =====================================================
@app.post("/predict")
def predict(
    transaction: Transaction,
    model_name: str = Query(
        "lightgbm",
        enum=["lightgbm", "xgboost", "decision_tree"]
    )
):
    pipeline = MODELS[model_name]

    X = pd.DataFrame(
        [[getattr(transaction, c) for c in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS
    )

    prob = pipeline.predict_proba(X)[0][1]
    threshold = float(os.getenv("FRAUD_THRESHOLD", 0.5))

    return {
        "model": model_name,
        "fraud_probability": float(prob),
        "is_fraud": bool(prob >= threshold)
    }

# =====================================================
# BATCH PREDICTION
# =====================================================
@app.post("/predict/batch")
def predict_batch(
    file: UploadFile = File(...),
    model_name: str = Query(
        "lightgbm",
        enum=["lightgbm", "xgboost", "decision_tree"]
    )
):
    pipeline = MODELS[model_name]
    df = pd.read_csv(file.file)

    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(400, f"Missing columns: {missing}")

    X = df[FEATURE_COLUMNS]
    probs = pipeline.predict_proba(X)[:, 1]
    threshold = float(os.getenv("FRAUD_THRESHOLD", 0.5))

    return {
        "model": model_name,
        "total_rows": len(df),
        "fraud_predictions": [
            {
                "row_id": i,
                "fraud_probability": float(p),
                "is_fraud": bool(p >= threshold)
            }
            for i, p in enumerate(probs)
        ]
    }

# =====================================================
# EXPLAINABILITY (LIGHTGBM)
# =====================================================
@app.post("/predict/explain")
def explain(transaction: Transaction, top_k: int = 5):
    if SHAP_EXPLAINER is None:
        raise HTTPException(500, "SHAP not available")

    pipeline = MODELS["lightgbm"]

    X = pd.DataFrame(
        [[getattr(transaction, c) for c in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS
    )

    prob = pipeline.predict_proba(X)[0][1]

    shap_values = SHAP_EXPLAINER.shap_values(X)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    shap_row = shap_values[0]
    shap_dict = dict(zip(FEATURE_COLUMNS, shap_row))

    top_features = dict(
        sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:top_k]
    )

    return {
        "model": "lightgbm",
        "fraud_probability": float(prob),
        "top_contributing_features": {
            k: float(v) for k, v in top_features.items()
        }
    }

# =====================================================
# HYBRID PREDICTION (ML + ISO + KNN)
# =====================================================
@app.post("/predict/hybrid")
def predict_hybrid(
    transaction: Transaction,
    model_name: str = Query(
        "lightgbm",
        enum=["lightgbm", "xgboost", "decision_tree"]
    )
):
    pipeline = MODELS[model_name]

    X = pd.DataFrame(
        [[getattr(transaction, c) for c in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS
    )

    prob = pipeline.predict_proba(X)[0][1]

    iso_anomaly = False
    if ISO_MODEL is not None:
        iso_anomaly = ISO_MODEL.predict(X)[0] == -1

    knn_anomaly = False
    knn_distance = None
    if KNN_MODEL is not None:
        X_scaled = KNN_SCALER.transform(X)
        distances, _ = KNN_MODEL.kneighbors(X_scaled)
        knn_distance = float(distances.mean())
        knn_anomaly = knn_distance > 3.0

    threshold = float(os.getenv("FRAUD_THRESHOLD", 0.5))

    return {
        "model": model_name,
        "fraud_probability": float(prob),
        "isolation_forest_anomaly": iso_anomaly,
        "knn_anomaly": knn_anomaly,
        "knn_distance": knn_distance,
        "final_decision": bool(prob >= threshold or iso_anomaly or knn_anomaly)
    }

# =====================================================
# HEALTH CHECK
# =====================================================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "models_loaded": list(MODELS.keys()),
        "iso_loaded": ISO_MODEL is not None,
        "knn_loaded": KNN_MODEL is not None
    }
