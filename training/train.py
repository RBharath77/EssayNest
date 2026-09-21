from pathlib import Path
import joblib
import numpy as np
from scipy.sparse import load_npz
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).resolve().parents[1]
A = ROOT/"training"/"artifacts"
M = ROOT/"models"
M.mkdir(exist_ok=True)

X = load_npz(A/"X_train.npz")
y = np.load(A/"y_train.npy")

model = LinearRegression()
model.fit(X, y)
joblib.dump(model, M/"linear_regression.pkl")
print("Saved models/linear_regression.pkl")
