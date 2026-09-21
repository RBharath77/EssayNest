# EssayScorer — AI-Based Automated Essay Scoring & Intelligent Writing Analytics

A full-stack essay evaluation workspace built with **Python, NLP, TF-IDF, Linear Regression, FastAPI, React/Vite, SQLite and ReportLab**.

## What is included

- Real essay scoring model trained on the included ASAP-style dataset (`full_text` → `score`).
- TF-IDF + 15 linguistic/text features.
- Held-out evaluation metrics in `training/artifacts/evaluation.json`.
- Login and registration with PBKDF2 password hashing and JWT sessions.
- Secure password reset flow with one-time, 30-minute tokens.
- Real reset-email support through SMTP (Gmail App Password supported).
- Essay input plus TXT/PDF/DOCX upload.
- Writing analytics and topic-overlap signal.
- Rule-based natural-writing revision generation for clarity, sentence variety and coherence.
- History with open/delete actions.
- Visually enhanced multi-page PDF reports.
- Dark mode and responsive React UI.

## 1. Setup

### macOS / Linux

```bash
cd EssayScorer-Complete-Ready
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
cd EssayScorer-Complete-Ready
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Model

The ZIP contains the trained model and evaluation artifacts, so you can start the backend directly.

To retrain from the included dataset:

```bash
python training/preprocessing.py
python training/feature_engineering.py
python training/train.py
python training/evaluate.py
```

The feature pipeline uses a stratified 8,000-row cap by default for fast local training. Set `MAX_TRAIN_ROWS` if you want to train on a different number of rows.

```bash
MAX_TRAIN_ROWS=12000 python training/feature_engineering.py
```

The included model was evaluated on a held-out 1,600-row test split. See `training/artifacts/evaluation.json` for the measured RMSE, MAE and R².

## 3. Password-reset email setup

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

For Gmail, enable 2-Step Verification and create a **Google App Password**. Use that App Password as `SMTP_PASSWORD`; do not use your normal Gmail password.

Example:

```env
JWT_SECRET=use-a-long-random-secret
FRONTEND_URL=http://localhost:5173
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_FROM=your-email@gmail.com
```

When SMTP is configured, the forgot-password endpoint sends a real email containing a link like:

`http://localhost:5173/?reset_token=<one-time-token>`

The token expires after 30 minutes and is invalidated after use.

If SMTP is not configured, local development mode returns a `development_reset_link` in the API response so the flow can still be tested. Do not use that fallback in production.

## 4. Start backend

```bash
source venv/bin/activate
uvicorn backend.app.main:app --reload
```

Backend:

`http://127.0.0.1:8000`

Swagger:

`http://127.0.0.1:8000/docs`

Health:

`http://127.0.0.1:8000/health`

## 5. Start frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

`http://localhost:5173`

Optional API override:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Score scale

The included ASAP-style training scores are on a 1–6 scale. The application normalizes the model output to a **1–10 display scale** while preserving the raw model score in the evaluation analysis. This is a presentation transformation, not a claim that the source dataset itself uses a 10-point scale.

## Natural-writing revision

The Humanized / Natural-Writing module is intentionally transparent and rule-based. It can shorten common wordy phrases, suggest sentence variety, flag repeated wording and suggest transitions. It is designed to improve clarity and readability; it is **not** an AI-detector bypass or an authorship-concealment feature.

## PDF report

The generated report contains:

1. Cover and overall score card
2. Writing snapshot
3. Visual metric bars
4. Topic relevance
5. Model information
6. Generated natural-writing revision
7. Revision suggestions
8. Original essay reference
9. Report methodology note

## Troubleshooting

### `Failed to fetch`

Make sure the backend is running first:

```bash
uvicorn backend.app.main:app --reload
```

Then verify:

`http://127.0.0.1:8000/health`

### Pylance says `numpy`, `joblib`, `sklearn`, etc. cannot be resolved

Select the project interpreter:

`EssayScorer-Complete-Ready/venv/bin/python`

Then reload VS Code.

### `Marks unavailable`

Check:

```bash
ls -lh models/
```

You should see `linear_regression.pkl` and `tfidf_vectorizer.pkl`.
