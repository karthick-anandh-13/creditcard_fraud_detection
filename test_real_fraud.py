import pandas as pd
import requests

df = pd.read_csv("data/raw/creditcard.csv")

fraud_txn = df[df["Class"] == 1].iloc[0]
normal_txn = df[df["Class"] == 0].iloc[0]

def test(txn, label):
    payload = txn.drop("Class").to_dict()
    r = requests.post(
        "http://127.0.0.1:8000/predict",
        json=payload
    )
    print(label, r.json())

test(normal_txn, "NORMAL")
test(fraud_txn, "FRAUD")
