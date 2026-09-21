from pathlib import Path
import re
import pandas as pd
import nltk

ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "dataset"
OUTPUT = DATASET_DIR / "cleaned_essays.csv"

def clean_text(text: str) -> str:
    text = re.sub(r"<.*?>", " ", str(text))
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def find_column(df, candidates):
    mapping = {str(c).strip().lower(): c for c in df.columns}
    for c in candidates:
        if c in mapping:
            return mapping[c]
    return None

def main():
    candidates = [
        DATASET_DIR / "essay_dataset.csv",
        DATASET_DIR / "ASAP_2_Final_github_train.csv"
    ]
    dataset = next((p for p in candidates if p.exists()), None)
    if dataset is None:
        csvs = [p for p in DATASET_DIR.glob("*.csv") if p.name != OUTPUT.name]
        dataset = csvs[0] if csvs else None
    if dataset is None:
        raise FileNotFoundError("Put an authorized CSV in dataset/essay_dataset.csv")

    df = pd.read_csv(dataset)
    essay_col = find_column(df, ["essay", "essay_text", "text", "full_text"])
    score_col = find_column(df, ["score", "domain1_score", "essay_score"])
    if not essay_col or not score_col:
        raise ValueError(f"Essay/score columns not found. Columns: {list(df.columns)}")

    out = df[[essay_col, score_col]].copy()
    out.columns = ["essay", "score"]
    out["essay"] = out["essay"].fillna("").astype(str).str.strip()
    out["score"] = pd.to_numeric(out["score"], errors="coerce")
    out = out.dropna(subset=["score"])
    out = out[out["essay"].str.len() > 0]
    out = out.drop_duplicates("essay").reset_index(drop=True)
    out["clean_essay"] = out["essay"].map(clean_text)
    out.to_csv(OUTPUT, index=False)
    print(f"Saved {len(out)} rows -> {OUTPUT}")

if __name__ == "__main__":
    main()
