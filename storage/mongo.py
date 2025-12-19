from pymongo import MongoClient

# Default local MongoDB
MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)

db = client["fraud_db"]

# Collections
velocity_collection = db["velocity_state"]
