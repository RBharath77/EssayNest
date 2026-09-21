# EssayScorer Complete Integrated Edition

This edition keeps the authentication, prediction, NLP analysis, natural-writing revision and PDF report pipeline, and restores the missing product modules: Dashboard, Evaluation, Analysis, History, Documents, Writing Quiz, My Reports, Writing Coach and Settings.

All module navigation is wired to FastAPI endpoints and SQLite persistence. Dashboard metrics are derived from stored evaluations; quiz attempts are persisted; documents can be uploaded/opened/deleted; reports download the actual evaluation PDF; and analysis uses the selected evaluation.

## Run
Backend: `source venv/bin/activate && python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`
Frontend: `cd frontend && npm install && npm run dev`


## UI cleanup in this build
- Writing Coach navigation and frontend module removed.
- Analytics and Humanize are rendered once each.
- Restart Vite after replacing the project to avoid serving an old bundle.

## Registration Welcome Email

After a successful registration, EssayScorer attempts to send a welcome email to the newly registered email address. The account is **not** logged in automatically: the user is returned to the sign-in screen and must enter the registered email and password.

Configure SMTP in a local `.env` file (copy `.env.example`):

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_FROM=your-email@gmail.com
```

For Gmail, use a Google **App Password**, not your normal Gmail password. The application never emails the user's password. The registration response contains `email_sent` so the frontend can show whether the welcome email was successfully sent.
