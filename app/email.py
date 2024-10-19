from email.message import EmailMessage

import aiosmtplib

from .config import settings

# For now, this is implemented as a simple prototype; in the future, 
# it will be implemented using background tasks.
async def send_reset_email(to_email: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    async with aiosmtplib.SMTP(
        hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, use_tls=False
    ) as smtp:
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        await smtp.send_message(message)
