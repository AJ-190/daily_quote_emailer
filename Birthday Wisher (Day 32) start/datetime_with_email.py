import datetime as dt
import smtplib
import time
import os
from email.mime.text import MIMEText
import random


class Email:
    def __init__(self, to_email):
        self.my_email = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")
        self.from_name = os.getenv("FROM_NAME", "CoreNerve.AI")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.to_email = to_email

        if not self.my_email or not self.password:
            raise ValueError(
                "Missing required environment variables: EMAIL_USER and EMAIL_PASS. "
                "Set them locally or in GitHub Actions secrets."
            )

    def get_random_quote(self):
        with open(os.path.join(os.path.dirname(__file__), "quotes.txt"), "r") as file:
            quotes = [line.strip() for line in file.readlines()]
        return random.choice(quotes)

    def message_preparation(self):
        subject = "Grow Your Inner World"
        quote = self.get_random_quote()
        html_body = f"""
        <html>
        <body style="font-family: Arial; background:#f4f7fb; padding:20px;">
            <div style="max-width:600px; margin:auto; background:#fff; padding:20px; border-radius:10px;">
                <h2 style="color:#2b5cbf;">Daily Motivation</h2>
                <p style="font-size:18px;">{quote}</p>
                <p style="color:gray;">— {self.from_name} | Keep shining and keep growing</p>
            </div>
        </body>
        </html>
        """
        msg = MIMEText(html_body, 'html')
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.my_email}>"
        msg["To"] = self.to_email
        return msg

    def send_email(self):
        msg = self.message_preparation()
        for attempt in range(5):
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as conn:
                    conn.login(self.my_email, self.password)
                    conn.sendmail(
                        from_addr=self.my_email,
                        to_addrs=self.to_email,
                        msg=msg.as_string()
                    )
                print(f"Email sent to {self.to_email} successfully ✅")
                break
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed for {self.to_email}: {e}")
                time.sleep(10)


if __name__ == "__main__":
    recipients_env = os.getenv("RECIPIENTS")
    if recipients_env:
        # Support comma or newline-separated emails
        recipients = [email.strip() for email in recipients_env.replace(',', '\n').split('\n') if email.strip()]
    else:
        # Fall back to emails.txt if RECIPIENTS env var not set
        with open(os.path.join(os.path.dirname(__file__), "emails.txt"), "r") as f:
            recipients = [line.strip() for line in f if line.strip()]

    for recipient in recipients:
        now = dt.datetime.now()
        weekday = now.weekday()
        if weekday in [1, 3, 6]:  # Tuesday, Thursday, Sunday
            email = Email(recipient)
            email.send_email()