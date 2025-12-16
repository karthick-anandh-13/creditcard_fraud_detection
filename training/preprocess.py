import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.utils.class_weight import compute_class_weight
import joblib

from data.schema import FEATURE_COLUMNS, TARGET_COLUMN

DATA_PATH = "data/raw/creditcard.csv"
ARTIFACT_PATH = "models/preprocessor.pkl"

def build_preprocessor():
    scaler = StandardScaler()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", scaler, FEATURE_COLUMNS)
        ],
        remainder="drop"
    )

    return preprocessor


def main():
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    preprocessor = build_preprocessor()
    preprocessor.fit(X_train)

    joblib.dump(preprocessor, ARTIFACT_PATH)

    print("Preprocessor saved to:", ARTIFACT_PATH)
    print("Train shape:", X_train.shape)
    print("Test shape:", X_test.shape)


if __name__ == "__main__":
    main()
