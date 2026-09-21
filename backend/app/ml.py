from pathlib import Path
import re
import joblib
import numpy as np
from scipy.sparse import hstack, csr_matrix
from .config import MODEL_DIR

class EssayModel:
    def __init__(self):
        self.model_path = MODEL_DIR/"linear_regression.pkl"
        self.vectorizer_path = MODEL_DIR/"tfidf_vectorizer.pkl"
        if not self.model_path.exists() or not self.vectorizer_path.exists():
            self.available = False
            self.model = None
            self.vectorizer = None
        else:
            self.available = True
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)

    @staticmethod
    def clean(text):
        text = re.sub(r"<.*?>", " ", str(text)).lower()
        text = re.sub(r"[^a-zA-Z\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def features(text):
        text = str(text)
        words = re.findall(r"\b[\w']+\b", text)
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
        lens = [len(w) for w in words]
        wc, cc, sc = len(words), len(text), len(sentences)
        uw = len(set(w.lower() for w in words))
        punct = sum(text.count(x) for x in ",.!?;:")
        return [
            wc, cc, sc, max(1,len(paragraphs)),
            wc/sc if sc else 0,
            sum(lens)/wc if wc else 0,
            uw, uw/wc if wc else 0,
            text.count(","), text.count("."), text.count("?"), text.count("!"),
            punct, punct/cc if cc else 0,
            sum(len(w)>=7 for w in words)/wc if wc else 0
        ]

    def predict(self, essay):
        if not self.available:
            raise RuntimeError("Trained model is not available. Run the training pipeline first.")
        processed = self.clean(essay)
        tfidf = self.vectorizer.transform([processed])
        numeric = csr_matrix(np.array([self.features(essay)], dtype=float))
        x = hstack([tfidf, numeric]).tocsr()
        return float(self.model.predict(x)[0])
