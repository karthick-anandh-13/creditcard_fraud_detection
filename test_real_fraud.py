import pandas as pd
df = pd.read_csv("data/raw/upi_transactions.csv")
print(df.head())
print(df.describe())
