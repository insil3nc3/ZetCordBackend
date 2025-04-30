import asyncio
from email.message import EmailMessage
import aiosmtplib
from app.core.config import settings

def render_email_template(code: int) -> str:
    with open("app/HTML/code_verif_mail.html", "r", encoding="utf-8") as f:
        return f.read().format(code=code)

async def send_code_async(recipient, subject, code):
    html_content = render_email_template(code)

    message = EmailMessage()
    message["From"] = settings.email_login
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content("Это HTML письмо, пожалуйста, откройте его в email-клиенте с поддержкой HTML.")
    message.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname="smtp.yandex.ru",
            port=465,
            use_tls=True,
            username=settings.email_login,
            password=settings.email_password
        )
        return 1
    except Exception:
        return -1
