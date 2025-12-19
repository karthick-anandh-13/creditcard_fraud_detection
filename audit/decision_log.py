# audit/decision_log.py

import json
from pathlib import Path
from datetime import datetime
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "audit" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "decision_log.jsonl"


# --------------------------------------------------
# SAFE JSON SERIALIZER
# --------------------------------------------------
def _json_serializer(obj: Any):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


# --------------------------------------------------
# AUDIT LOG WRITER
# --------------------------------------------------
def log_decision(record: dict):
    """
    Writes one fraud decision record per line (JSONL).
    Safely serializes datetime and other non-JSON objects.
    """

    # Ensure audit timestamp exists
    record.setdefault(
        "logged_at",
        datetime.utcnow()
    )

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            json.dumps(record, default=_json_serializer) + "\n"
        )
