import smtplib
from email.mime.text import MIMEText

from backend.config import Config


def send_email(to_address, subject, body, html=False):
    """
    Sends a real email if SMTP settings are configured via environment
    variables; otherwise prints to the console so reminders/reports are
    testable without a real mail account.
    """
    if not Config.SMTP_HOST:
        print(f"[EMAIL - console mode] To: {to_address} | Subject: {subject}\n{body}\n")
        return

    msg = MIMEText(body, "html" if html else "plain")
    msg["Subject"] = subject
    msg["From"] = Config.SMTP_FROM
    msg["To"] = to_address

    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.sendmail(Config.SMTP_FROM, [to_address], msg.as_string())