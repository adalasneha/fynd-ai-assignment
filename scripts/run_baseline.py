# scripts/run_baseline.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")


import time
import json
import random
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# Import your OpenRouter helper (must exist at app/llm_openrouter.py)
from app.llm_openrouter import call_llm

DATA_PATH = Path("data/sample_yelp.csv")
OUT_DIR = Path("results")
OUT_DIR.mkdir(exist_ok=True)
OUT_CSV = OUT_DIR / "baseline_results.csv"

PROMPT_TEMPLATE = """You are a classifier that reads a Yelp review and predicts a star rating from 1 to 5.
Return ONLY a JSON object with this structure:
{{
  "predicted_stars": <int>,
  "explanation": "<short reason>"
}}

Review:
"{review_text}"
"""

def safe_json_parse(text):
    """Try to parse JSON; if fails, try extract first {...} substring."""
    if not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except Exception:
        import re
        m = re.search(r'(\{.*\})', text, flags=re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                return None
        return None

def single_call_with_retries(prompt, retries=2, backoff=1.0):
    for attempt in range(retries+1):
        try:
            out = call_llm(prompt)
            return out
        except Exception as e:
            if attempt < retries:
                sleep = backoff * (2**attempt) + random.random()*0.5
                time.sleep(sleep)
                continue
            else:
                raise

def main(sleep_between=0.25):
    df = pd.read_csv(DATA_PATH)
    results = []
    for idx, row in tqdm(df.reset_index(drop=True).iterrows(), total=len(df)):
        review = str(row["review"])
        gold = int(row["stars"])
        prompt = PROMPT_TEMPLATE.replace("{review_text}", review.replace('"', '\\"'))
        try:
            raw_out = single_call_with_retries(prompt, retries=2)
        except Exception as e:
            raw_out = f"__CALL_FAILED__ {repr(e)}"
        parsed = safe_json_parse(raw_out)
        pred = None
        valid = False
        if parsed and "predicted_stars" in parsed:
            try:
                pred = int(parsed["predicted_stars"])
                valid = True
            except Exception:
                valid = False
        results.append({
            "idx": idx,
            "review": review,
            "gold": gold,
            "raw_output": raw_out,
            "parsed_json": json.dumps(parsed, ensure_ascii=False) if parsed else "",
            "predicted": pred,
            "valid_json": valid
        })
        time.sleep(sleep_between)  # rate limit friendly

    out_df = pd.DataFrame(results)
    out_df.to_csv(OUT_CSV, index=False)
    print(f"Saved results to {OUT_CSV}")

    # Metrics (only for valid JSON rows)
    valid_mask = out_df["valid_json"]
    n_total = len(out_df)
    n_valid = valid_mask.sum()
    acc = None
    mae = None
    if n_valid > 0:
        acc = (out_df.loc[valid_mask, "predicted"] == out_df.loc[valid_mask, "gold"]).mean()
        mae = (out_df.loc[valid_mask, "predicted"] - out_df.loc[valid_mask, "gold"]).abs().mean()
    print("Total samples:", n_total)
    print("Valid JSON predictions:", int(n_valid), f"({n_valid/n_total:.2%})")
    if acc is not None:
        print(f"Accuracy (valid only): {acc:.4f}")
        print(f"MAE (valid only): {mae:.4f}")
    else:
        print("No valid JSON predictions to report metrics.")

if __name__ == "__main__":
    main(sleep_between=0.25)
