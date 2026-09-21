import os
import smtplib
from email.message import EmailMessage


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("SMTP_FROM", username).strip()

    if not all([host, username, password, sender]):
        # Development mode: caller can still log/use the generated link.
        return False

    msg = EmailMessage()
    msg["Subject"] = "Reset your EssayScorer password"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(
        "EssayScorer password reset\n\n"
        "We received a request to reset your password. Open the link below "
        "within 30 minutes to create a new password:\n\n"
        f"{reset_link}\n\n"
        "If you did not request this, you can safely ignore this email."
    )

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(username, password)
        server.send_message(msg)
    return True


def send_welcome_email(to_email: str, user_name: str) -> bool:
    """Send a welcome email after a successful account registration."""
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("SMTP_FROM", username).strip()

    if not all([host, username, password, sender]):
        return False

    msg = EmailMessage()
    msg["Subject"] = "Welcome to EssayScorer"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(
        f"Hi {user_name},\n\n"
        "Welcome to EssayScorer! Your account has been created successfully.\n\n"
        "You can now sign in using the email address and password you registered with. "
        "Your password is never included in email messages.\n\n"
        "EssayScorer helps you evaluate essays, explore writing analytics, improve drafts "
        "with natural-writing suggestions, save documents, and generate PDF reports.\n\n"
        "See you inside EssayScorer!\n"
    )

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(username, password)
        server.send_message(msg)
    return True
