from pymongo import MongoClient
from pathlib import Path
import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017"
)

client = MongoClient(MONGO_URI)

db = client["fraud_db"]

# Collections
velocity_col = db["velocity_state"]
risk_profile_col = db["risk_profiles"]
graph_edges_col = db["graph_edges"]
audit_col = db["audit_logs"]
feedback_col = db["fraud_feedback"]
