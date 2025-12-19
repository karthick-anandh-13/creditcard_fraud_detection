# state/threshold_controller.py

from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = BASE_DIR / "state" / "data"
STATE_DIR.mkdir(parents=True, exist_ok=True)

THRESHOLD_FILE = STATE_DIR / "adaptive_thresholds.json"

DEFAULT_THRESHOLDS = {
    "BLOCK": 0.85,
    "STEP_UP": 0.45
}


def load_thresholds():
    if not THRESHOLD_FILE.exists():
        save_thresholds(DEFAULT_THRESHOLDS)
        return DEFAULT_THRESHOLDS.copy()

    with open(THRESHOLD_FILE, "r") as f:
        return json.load(f)


def save_thresholds(thresholds: dict):
    with open(THRESHOLD_FILE, "w") as f:
        json.dump(thresholds, f, indent=2)


def adjust_global_thresholds(reason: str):
    thresholds = load_thresholds()

    if reason == "FRAUD_LEAKAGE":
        thresholds["BLOCK"] = max(0.60, thresholds["BLOCK"] - 0.05)
        thresholds["STEP_UP"] = max(0.30, thresholds["STEP_UP"] - 0.05)

    elif reason == "CUSTOMER_FRICTION":
        thresholds["BLOCK"] = min(0.95, thresholds["BLOCK"] + 0.05)
        thresholds["STEP_UP"] = min(0.70, thresholds["STEP_UP"] + 0.05)

    save_thresholds(thresholds)

    print(
        f"[GLOBAL THRESHOLD UPDATE] reason={reason} | "
        f"BLOCK={thresholds['BLOCK']:.2f} | "
        f"STEP_UP={thresholds['STEP_UP']:.2f}"
    )
