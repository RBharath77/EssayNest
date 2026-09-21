from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import re
from scipy.sparse import hstack, csr_matrix, save_npz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
CLEANED = ROOT / "dataset" / "cleaned_essays.csv"
MODEL_DIR = ROOT / "models"
ARTIFACTS = ROOT / "training" / "artifacts"
MODEL_DIR.mkdir(exist_ok=True)
ARTIFACTS.mkdir(exist_ok=True)

NUMERIC_COLUMNS = [
    "word_count", "character_count", "sentence_count", "paragraph_count",
    "avg_sentence_length", "avg_word_length", "unique_word_count",
    "vocabulary_richness", "comma_count", "period_count", "question_count",
    "exclamation_count", "punctuation_count", "punctuation_density", "long_word_ratio"
]


def extract_numeric_features(text):
    text = str(text)
    words = re.findall(r"\b[\w']+\b", text)
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    lengths = [len(w) for w in words]
    wc = len(words); cc = len(text); sc = len(sentences); pc = max(1, len(paragraphs))
    uw = len(set(w.lower() for w in words)); punct = sum(text.count(x) for x in ",.!?;:")
    return [wc, cc, sc, pc, wc/sc if sc else 0, sum(lengths)/wc if wc else 0,
            uw, uw/wc if wc else 0, text.count(","), text.count("."), text.count("?"),
            text.count("!"), punct, punct/cc if cc else 0, sum(len(w)>=7 for w in words)/wc if wc else 0]


def stratified_cap(df, max_rows=8000):
    if len(df) <= max_rows:
        return df
    parts=[]
    for _, group in df.groupby("score", sort=True):
        n=max(1, round(max_rows * len(group) / len(df)))
        parts.append(group.sample(n=min(n,len(group)), random_state=42))
    out=pd.concat(parts).sample(frac=1, random_state=42).reset_index(drop=True)
    return out.head(max_rows)


def main():
    if not CLEANED.exists():
        raise FileNotFoundError("Run preprocessing.py first.")
    df = pd.read_csv(CLEANED)
    df = stratified_cap(df, int(__import__('os').getenv("MAX_TRAIN_ROWS", "8000")))
    X_text = df["clean_essay"].fillna("")
    X_num = np.asarray([extract_numeric_features(x) for x in df["essay"]], dtype=np.float32)
    y = df["score"].astype(np.float32).to_numpy()

    Xtr_t, Xte_t, Xtr_n, Xte_n, ytr, yte = train_test_split(
        X_text, X_num, y, test_size=0.20, random_state=42, stratify=y
    )
    vectorizer = TfidfVectorizer(max_features=800, ngram_range=(1,1), min_df=2, sublinear_tf=True, dtype=np.float32)
    tr_tfidf = vectorizer.fit_transform(Xtr_t)
    te_tfidf = vectorizer.transform(Xte_t)
    X_train = hstack([tr_tfidf, csr_matrix(Xtr_n)]).tocsr()
    X_test = hstack([te_tfidf, csr_matrix(Xte_n)]).tocsr()

    save_npz(ARTIFACTS/"X_train.npz", X_train)
    save_npz(ARTIFACTS/"X_test.npz", X_test)
    np.save(ARTIFACTS/"y_train.npy", ytr)
    np.save(ARTIFACTS/"y_test.npy", yte)
    joblib.dump(vectorizer, MODEL_DIR/"tfidf_vectorizer.pkl")
    joblib.dump(NUMERIC_COLUMNS, MODEL_DIR/"numeric_features.pkl")

    metadata={"numeric_features":NUMERIC_COLUMNS,"tfidf_features":int(tr_tfidf.shape[1]),"total_features":int(X_train.shape[1]),"train_rows":int(X_train.shape[0]),"test_rows":int(X_test.shape[0]),"training_rows_capped":len(df)}
    (ARTIFACTS/"feature_metadata.json").write_text(json.dumps(metadata, indent=2))
    print(metadata)

if __name__ == "__main__": main()
