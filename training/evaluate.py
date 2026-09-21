from pathlib import Path
import json
import joblib
import numpy as np
from scipy.sparse import load_npz
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
A = ROOT/"training"/"artifacts"
M = ROOT/"models"

model = joblib.load(M/"linear_regression.pkl")
X = load_npz(A/"X_test.npz")
y = np.load(A/"y_test.npy")
pred = model.predict(X)

metrics = {
    "rmse": float(np.sqrt(mean_squared_error(y, pred))),
    "mae": float(mean_absolute_error(y, pred)),
    "r2": float(r2_score(y, pred)),
    "test_rows": int(len(y))
}
(A/"evaluation.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))
