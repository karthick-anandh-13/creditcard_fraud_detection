import joblib
from sklearn.pipeline import Pipeline
from lightgbm import LGBMClassifier

from training.utils import load_data, evaluate_model

PREPROCESSOR_PATH = "models/preprocessor.pkl"
MODEL_PATH = "models/fraud_lgbm.pkl"

def main():
    X_train, X_test, y_train, y_test = load_data()

    preprocessor = joblib.load(PREPROCESSOR_PATH)

    lgbm_model = LGBMClassifier(
        n_estimators=600,
        learning_rate=0.05,
        num_leaves=64,
        max_depth=-1,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", lgbm_model)
        ]
    )

    print("Training LightGBM...")
    pipeline.fit(X_train, y_train)

    evaluate_model(pipeline, X_test, y_test, "LightGBM")

    joblib.dump(pipeline, MODEL_PATH)
    print("Saved LightGBM model to:", MODEL_PATH)


if __name__ == "__main__":
    main()
