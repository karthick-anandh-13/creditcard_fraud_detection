# evaluation/compare_models_file.py

import json
from pathlib import Path

AUDIT_LOG = Path("audit_logs/upi_decisions.log")

def evaluate():
    if not AUDIT_LOG.exists():
        print("❌ Audit log not found")
        return

    total = 0
    champ_hits = 0
    chall_hits = 0
    champ_fp = 0
    chall_fp = 0

    with open(AUDIT_LOG, "r") as f:
        for line in f:
            record = json.loads(line)
            if "actual_outcome" not in record:
                continue

            total += 1
            actual = record["actual_outcome"]      # FRAUD / GENUINE
            champ = record.get("decision")
            chall = record.get("challenger_decision")

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

    print("\n📊 CHAMPION vs CHALLENGER EVALUATION (FILE)")
    print("-" * 50)
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
