import json
from pathlib import Path

QUEUE_FILE = Path("queue/upi_events.jsonl")


def push_event(event: dict):
    QUEUE_FILE.parent.mkdir(exist_ok=True)
    with open(QUEUE_FILE, "a") as f:
        f.write(json.dumps(event, default=str) + "\n")


def read_events():
    if not QUEUE_FILE.exists():
        return []

    with open(QUEUE_FILE, "r") as f:
        return [json.loads(line) for line in f]


def clear_queue():
    if QUEUE_FILE.exists():
        QUEUE_FILE.unlink()
