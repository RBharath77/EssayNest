# EssayScorer Email Setup

EssayScorer now sends a welcome email automatically after a successful account registration.

## Registration flow

1. User creates an account.
2. The account is saved in SQLite.
3. EssayScorer attempts to send a welcome email to the registered email address.
4. The user is returned to the login screen.
5. The user must log in using the registered email and password.
6. The user's password is never sent by email.

## Gmail SMTP

Create a local `.env` file in the project root by copying `.env.example` and set:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_FROM=your-email@gmail.com
```

Use a Google App Password rather than your normal Gmail password.

Restart FastAPI after changing `.env`:

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

## Other SMTP providers

Replace `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM` with the SMTP settings supplied by your email provider.

## If SMTP is not configured

Registration still succeeds and the user is **not** automatically logged in. The API returns `email_sent: false`, and the frontend tells the user that the account was created but an email could not be sent because SMTP is not configured/available.
