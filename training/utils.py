import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report

from data.schema import FEATURE_COLUMNS, TARGET_COLUMN

DATA_PATH = "data/raw/creditcard.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    return train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )


def evaluate_model(model, X_test, y_test, model_name="model"):
    y_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_proba)

    print(f"\n{model_name} ROC-AUC: {auc:.4f}")
    print("\nClassification Report (threshold=0.5):")
    print(classification_report(y_test, (y_proba >= 0.5).astype(int)))
