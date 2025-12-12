from pathlib import Path
import pandas as pd
import threading

DATA_PATH = Path("data")
DATA_PATH.mkdir(parents=True, exist_ok=True)

SUBMISSIONS_CSV = DATA_PATH / "submissions.csv"
_lock = threading.Lock()

def _ensure_csv():
    if not SUBMISSIONS_CSV.exists():
        df = pd.DataFrame(columns=[
            "id",
            "timestamp",
            "user_rating",
            "user_review",
            "ai_response",
            "ai_summary",
            "ai_recommendations",
        ])
        df.to_csv(SUBMISSIONS_CSV, index=False)

def read_all():
    _ensure_csv()
    return pd.read_csv(SUBMISSIONS_CSV)

def append_submission(row: dict):
    _ensure_csv()
    with _lock:
        df = pd.read_csv(SUBMISSIONS_CSV)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(SUBMISSIONS_CSV, index=False)

def overwrite_df(df: pd.DataFrame):
    df.to_csv(SUBMISSIONS_CSV, index=False)
