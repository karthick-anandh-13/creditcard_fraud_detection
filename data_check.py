'''import pandas as pd

DATA_PATH = "data/raw/creditcard.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nFraud vs Non-Fraud distribution:")
print(df["Class"].value_counts())
print("\nFraud percentage:")
print(df["Class"].value_counts(normalize=True) * 100)'''


import joblib
import pandas as pd

preprocessor = joblib.load("models/preprocessor.pkl")
df = pd.read_csv("data/raw/creditcard.csv").head(5)

X_transformed = preprocessor.transform(df.drop(columns=["Class"]))
print(X_transformed.shape)
