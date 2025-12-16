import joblib
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from training.utils import load_data, evaluate_model

PREPROCESSOR_PATH = "models/preprocessor.pkl"
MODEL_PATH = "models/fraud_xgb.pkl"

def main():
    X_train, X_test, y_train, y_test = load_data()

    preprocessor = joblib.load(PREPROCESSOR_PATH)

    xgb_model = XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
        eval_metric="auc",
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", xgb_model)
        ]
    )

    print("Training XGBoost...")
    pipeline.fit(X_train, y_train)

    evaluate_model(pipeline, X_test, y_test, "XGBoost")

    joblib.dump(pipeline, MODEL_PATH)
    print("Saved XGBoost model to:", MODEL_PATH)


if __name__ == "__main__":
    main()
