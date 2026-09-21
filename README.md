# ✍️ Essayly — AI Essay Scoring & Writing Analytics

### 🔍 Natural Language Processing | Machine Learning | React | FastAPI

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![Status](https://img.shields.io/badge/Project-Completed-brightgreen.svg)

## 📌 Overview

**Essayly** is an AI-assisted full-stack essay evaluation and writing analytics platform built using **Natural Language Processing (NLP)**, **Machine Learning**, **React**, and **FastAPI**.

It helps students and learners understand their writing through automated essay scoring, detailed linguistic analysis, writing-improvement suggestions, evaluation history, document processing, analytics, and downloadable PDF reports.

## ✨ Features

- 📝 Automated essay scoring
- 🧠 NLP-based essay analysis
- 📊 Detailed writing analytics
- 🔢 15+ linguistic and text features
- 📚 TF-IDF feature extraction
- 🤖 Linear Regression ML prediction
- 📈 RMSE, MAE & R² model evaluation
- ✍️ Natural-writing improvement suggestions
- 📂 TXT / PDF / DOCX document support
- 📜 Evaluation history
- 📄 Downloadable PDF reports
- 🔐 JWT authentication
- 📧 Registration welcome email
- 🔑 Password reset support
- 🌗 Light & Dark themes
- ⚡ Persistent login across browser refresh
- 📱 Responsive web interface
- 🎨 Smooth modern UI animations

> The writing-improvement module is designed to improve clarity, readability, sentence variety, and natural phrasing rather than to hide authorship or bypass AI-detection systems.

## 🧠 How It Works

```text
Essay Input / File Upload
        ↓
Text Preprocessing
        ↓
Feature Extraction
        ↓
TF-IDF + Linguistic Features
        ↓
Linear Regression Model
        ↓
Predicted Essay Score
        ↓
Detailed Writing Analysis
        ↓
Improvement Suggestions
        ↓
History / Analytics / PDF Report
```

## 🤖 Machine Learning

Essayly combines **TF-IDF features** with numerical linguistic and text features to predict an essay score using **Linear Regression**.

### 🔢 Feature Examples

- Word Count
- Character Count
- Sentence Count
- Paragraph Count
- Average Sentence Length
- Average Word Length
- Unique Word Count
- Vocabulary Richness
- Comma Count
- Period Count
- Question Count
- Exclamation Count
- Punctuation Density
- Long-Word Ratio
- TF-IDF Features

### 📊 Evaluation Metrics

- RMSE — Root Mean Squared Error
- MAE — Mean Absolute Error
- R² — Coefficient of Determination

> Model performance should be reported using the results from the actual trained evaluation experiment.

## 📊 Writing Analysis

Essayly provides insights into:

- ✍️ Writing length
- 🧩 Sentence structure
- 📚 Vocabulary usage
- 🔤 Lexical diversity
- 🔎 Repetition patterns
- ❗ Punctuation patterns
- 📖 Readability-related characteristics
- 💡 Areas for writing improvement

## ✍️ Natural-Writing Improvement

The **Humanize** module focuses on improving writing quality through suggestions such as:

- Reducing unnecessary repetition
- Improving sentence variety
- Making wording clearer
- Improving transitions
- Encouraging active and natural phrasing

## 📂 Document Support

Essayly supports:

- `.txt`
- `.pdf`
- `.docx`

Uploaded documents can be processed through the essay evaluation workflow.

## 🔐 Authentication

Essayly includes:

- 👤 User registration
- 🔑 Login
- 🛡️ JWT authentication
- 🔒 Protected routes
- ⚡ Persistent session across browser refresh
- 📧 Registration welcome email
- 🔄 Password reset support

### Authentication Flow

```text
Create Account
      ↓
Account Created
      ↓
Welcome Email
      ↓
Login with Email + Password
      ↓
JWT Authentication
      ↓
Dashboard
```

## 🧩 Main Modules

| Module | Description |
|---|---|
| 📊 Dashboard | View recent evaluations and writing progress |
| 📝 New Essay | Write and submit a new essay |
| 🔍 Analysis | View detailed linguistic analysis |
| 📈 Analytics | Explore scores and writing trends |
| ✍️ Humanize | Improve clarity and natural phrasing |
| 📜 History | Review previous essay evaluations |
| 📂 Documents | Upload and manage essay files |
| 🧠 Writing Quiz | Practice writing-related concepts |
| 📄 My Reports | Generate and access PDF reports |
| ⚙️ Settings | Manage account and appearance |

## 🎨 UI & Theme

Essayly uses a writing-focused interface designed like a **modern digital writing studio**.

### ☀️ Light Theme

- Warm paper-inspired background
- Forest-green navigation
- Copper/gold accent details
- Clean editorial-style cards
- High readability

### 🌙 Dark Theme

- Deep pine and ink background
- Dark green surfaces
- Copper accent details
- Soft secondary highlights
- Comfortable contrast for longer writing sessions

The selected theme is saved locally and restored after browser refresh.

## 🛠️ Technologies Used

### Frontend

- React
- Vite
- JavaScript
- CSS
- Lucide React
- Recharts

### Backend

- Python
- FastAPI
- SQLite
- JWT
- ReportLab

### Machine Learning & NLP

- Scikit-Learn
- NumPy
- SciPy
- Joblib
- TF-IDF
- Linear Regression

### Document Processing

- PyPDF
- python-docx

## 📁 Project Structure

```text
Essayly/
│
├── dataset/
│
├── training/
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── train.py
│   ├── evaluate.py
│   └── artifacts/
│
├── models/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── nlp.py
│   │   ├── ml.py
│   │   └── report.py
│   │
│   └── tests/
│       └── test_api.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## 📁 Dataset

The model requires an essay dataset containing essay text and corresponding scores.

### Supported Text Columns

```text
essay
essay_text
text
full_text
```

### Supported Score Columns

```text
score
domain1_score
essay_score
```

> Keep the dataset structure consistent with the training scripts used in the repository.

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/RBharath77/EssayNest.git
cd EssayNest
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Train the Model

```bash
python training/preprocessing.py
python training/feature_engineering.py
python training/train.py
python training/evaluate.py
```

### 5. Start the FastAPI Backend

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API Documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the React Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open the Vite URL shown in the terminal.

## 📧 Email Configuration

Create a `.env` file and configure SMTP:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
FRONTEND_URL=http://localhost:5173
```

For Gmail, use an **App Password** instead of your normal account password.

Never commit real credentials to GitHub.

## 🧪 Testing

Run backend tests:

```bash
pytest backend/tests
```

Recommended checks include:

- Registration
- Login
- JWT authentication
- Protected routes
- Essay prediction
- Document upload
- Evaluation history
- PDF report generation
- Password reset
- Invalid input handling
- Theme persistence

## 🔌 API Endpoints

### Authentication

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Essay Evaluation

```text
POST /predict
POST /upload
```

### History

```text
GET /history
GET /evaluations/{evaluation_id}
```

### Reports

```text
POST /reports/{evaluation_id}
GET  /reports/{evaluation_id}
```

### Analytics & Dashboard

```text
GET /dashboard
GET /analytics
GET /model-metrics
```

### Other Modules

```text
POST /humanize
GET  /documents
GET  /quiz
POST /quiz/submit
GET  /quiz/history
```

## 🔄 Application Workflow

```text
Login
  ↓
Dashboard
  ↓
Write Essay / Upload Document
  ↓
Preprocessing
  ↓
NLP Feature Extraction
  ↓
ML Prediction
  ↓
Score + Writing Analysis
  ↓
Humanize / Improve Writing
  ↓
Save Evaluation
  ↓
Analytics + History
  ↓
Generate PDF Report
```

## 🚀 Future Improvements

- 🤖 Transformer-based essay scoring
- 🌐 Multilingual essay analysis
- 📚 Advanced rubric-based feedback
- 👨‍🏫 Teacher / faculty dashboard
- 🎯 Writing goal tracking
- ☁️ Cloud deployment
- 🧪 Model version tracking
- 🔎 Advanced topic relevance analysis
- 📖 More readability metrics
- 🎙️ Voice-based essay input

## 📸 Output

Add your application screenshots here:
<img width="1440" height="776" alt="Screenshot 2026-09-21 at 9 45 14 PM" src="https://github.com/user-attachments/assets/3a59906c-7857-4cca-a8c4-d05e60cf4158" />
<img width="1440" height="776" alt="Screenshot 2026-09-21 at 9 47 02 PM" src="https://github.com/user-attachments/assets/9f089d32-cd5e-4fc1-b2ed-8b7bf12f962c" />
<img width="1440" height="776" alt="Screenshot 2026-09-21 at 9 45 04 PM" src="https://github.com/user-attachments/assets/6d0a96cf-4fd0-400f-89e3-dd216ed05f77" />
<img width="1440" height="776" alt="Screenshot 2026-09-21 at 9 41 27 PM" src="https://github.com/user-attachments/assets/0e5fcd2d-056b-455a-902b-7cb84b52a843" />
<img width="1440" height="776" alt="Screenshot 2026-09-21 at 9 41 47 PM" src="https://github.com/user-attachments/assets/167e2f38-ac28-4ac5-8713-2a379673ace8" />
<img width="1440" height="776" alt="Screenshot 2026-09-21 at 9 49 17 PM" src="https://github.com/user-attachments/assets/231aa79f-fce0-4b2e-8761-017ea8e3835d" />
<img width="1440" height="776" alt="Screenshot 2026-09-21 at 9 42 21 PM" src="https://github.com/user-attachments/assets/82311114-5d02-4e18-8d69-8f0041115339" />
<img width="1440" height="776" alt="Screenshot 2026-09-21 at 9 50 04 PM" src="https://github.com/user-attachments/assets/0e9a435c-dbdf-414f-b78f-ad47e7341063" />



<!--## 🌐 Live Demo

👉 **[Launch Essayly](YOUR_LIVE_DEMO_URL)**

Try the Essayly AI essay scoring and writing analytics platform online.
-->
## 👨‍💻 Author

**Bharath R**

## 📄 License

This project is created for educational and academic purposes.

---

### 💡 Essayly

**Write. Analyze. Improve. ✍️🧠📊**
