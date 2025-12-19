# evaluation/compare_models_mongo.py

from storage.mongo import db

audit_col = db["audit_decisions"]

def evaluate():
    cursor = audit_col.find(
        {"actual_outcome": {"$exists": True}},
        {
            "decision": 1,
            "challenger_decision": 1,
            "actual_outcome": 1,
            "_id": 0
        }
    )

    total = 0
    champ_hits = 0
    chall_hits = 0
    champ_fp = 0
    chall_fp = 0

    for r in cursor:
        total += 1
        actual = r["actual_outcome"]
        champ = r.get("decision")
        chall = r.get("challenger_decision")

        if actual == "FRAUD":
            if champ == "BLOCK":
                champ_hits += 1
            if chall == "BLOCK":
                chall_hits += 1

        if actual == "GENUINE":
            if champ == "BLOCK":
                champ_fp += 1
            if chall == "BLOCK":
                chall_fp += 1

    print("\n📊 CHAMPION vs CHALLENGER EVALUATION (MONGO)")
    print("-" * 55)
    print(f"Total evaluated: {total}")
    print(f"Champion fraud caught: {champ_hits}")
    print(f"Challenger fraud caught: {chall_hits}")
    print(f"Champion false positives: {champ_fp}")
    print(f"Challenger false positives: {chall_fp}")

    if chall_hits > champ_hits and chall_fp <= champ_fp:
        print("\n✅ RECOMMENDATION: PROMOTE CHALLENGER")
    else:
        print("\n⚠️ RECOMMENDATION: KEEP CHAMPION")

if __name__ == "__main__":
    evaluate()
