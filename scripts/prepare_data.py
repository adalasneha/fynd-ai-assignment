import os
import pandas as pd
import random
from pathlib import Path

OUT_PATH = Path("data/sample_yelp.csv")
SRC_CANDIDATES = [
    Path("data/yelp_reviews.csv"),
    Path("data/reviews.csv"),
    Path("data/yelp_academic_dataset_review.csv"),
]

SYNTH_EXAMPLES = [
    ("The food was amazing and service was excellent.", 5),
    ("Terrible experience — cold food and rude staff.", 1),
    ("Decent place. Portion sizes were small but taste was good.", 3),
    ("Waited 45 minutes. Will not come back.", 1),
    ("Had a nice time; dessert was fantastic.", 5),
    ("Not worth the price.", 2),
    ("Staff was friendly but the food was average.", 3),
    ("Perfect for a quick lunch. Will return.", 4),
    ("Order was wrong and they didn't fix it.", 1),
    ("Great ambiance and prompt service.", 5),
]

def generate_synthetic(n=200):
    texts = []
    for i in range(n):
        base, star = random.choice(SYNTH_EXAMPLES)
        variation = ""
        if random.random() < 0.4:
            variation = " " + random.choice([
                "Loved it!", 
                "Not satisfied.", 
                "Could be better.", 
                "Highly recommend."
            ])
        texts.append({"review": f"{base}{variation}", "stars": star})
    return pd.DataFrame(texts)

def sample_from_file(src: Path, n=200):
    df = pd.read_csv(src, low_memory=False)
    df2 = df.sample(n=min(n, len(df)), random_state=42)
    df2 = df2.rename(columns={df2.columns[0]: "review", df2.columns[1]: "stars"})
    return df2[["review", "stars"]]

def main():
    for c in SRC_CANDIDATES:
        if c.exists():
            print(f"Found source dataset: {c}, sampling 200 rows...")
            df = sample_from_file(c)
            df.to_csv(OUT_PATH, index=False)
            print(f"Sample saved to {OUT_PATH}")
            return
    
    print("No dataset found. Generating synthetic sample instead...")
    df = generate_synthetic()
    df.to_csv(OUT_PATH, index=False)
    print(f"Synthetic dataset saved to {OUT_PATH}")

if __name__ == "__main__":
    main()
