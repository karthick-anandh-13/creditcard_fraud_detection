import pandas as pd
import joblib
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from data.schema import FEATURE_COLUMNS

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "creditcard.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)

X = df[FEATURE_COLUMNS]
y = df["Class"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Decision Tree (controlled depth to avoid overfitting)
dt_model = DecisionTreeClassifier(
    max_depth=6,
    min_samples_leaf=50,
    class_weight="balanced",
    random_state=42
)

dt_model.fit(X_train, y_train)

# Evaluation
y_pred = dt_model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(dt_model, MODEL_DIR / "fraud_decision_tree.pkl")

print("Decision Tree model trained and saved")
