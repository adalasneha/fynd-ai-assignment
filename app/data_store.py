from pathlib import Path
import pandas as pd
import json
import threading
import time
from datetime import datetime

DATA_PATH = Path("data")
DATA_PATH.mkdir(exist_ok=True)
SUBMISSIONS_CSV = DATA_PATH / "submissions.csv"

_lock = threading.Lock()

def _ensure_csv():
    if not SUBMISSIONS_CSV.exists():
        df = pd.DataFrame(columns=[
            "id","timestamp","user_rating","user_review",
            "ai_response","ai_summary","ai_recommendations"
        ])
        df.to_csv(SUBMISSIONS_CSV, index=False)

def read_all():
    _ensure_csv()
    return pd.read_csv(SUBMISSIONS_CSV)

def append_submission(row: dict):
    """Append a dict as a new row. row keys: id,timestamp,user_rating,user_review,ai_response,ai_summary,ai_recommendations"""
    _ensure_csv()
    # simple thread-safe append
    with _lock:
        df = pd.read_csv(SUBMISSIONS_CSV)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(SUBMISSIONS_CSV, index=False)

def overwrite_df(df: pd.DataFrame):
    """Replace CSV - used rarely."""
    df.to_csv(SUBMISSIONS_CSV, index=False)