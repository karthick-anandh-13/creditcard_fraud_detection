import pandas as pd

df = pd.read_csv("data/raw/creditcard.csv")
df.drop(columns=["Class"]).head(10).to_csv("sample_batch.csv", index=False)
print("sample_batch.csv created")
