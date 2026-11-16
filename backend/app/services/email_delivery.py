import smtplib,ssl
from email.message import EmailMessage
from urllib.parse import quote

class EmailDeliveryError(RuntimeError):pass
def send_account_token(settings,to_email:str,purpose:str,token:str)->None:
    if settings.environment=="development":return
    if not settings.smtp_host or not settings.smtp_from:raise EmailDeliveryError("Email delivery is not configured")
    page="verify-email" if purpose=="verify_email" else "reset-password"
    action=settings.public_url.rstrip("/")+"/"+page+"?token="+quote(token,safe="")
    subject="Verify your Vedic Astrology email" if purpose=="verify_email" else "Reset your Vedic Astrology password"
    message=EmailMessage();message["Subject"]=subject;message["From"]=settings.smtp_from;message["To"]=to_email
    message.set_content("Use this time-limited link to continue:\n\n"+action+"\n\nIf you did not request this, ignore this message.")
    try:
        if settings.smtp_port==465:
            with smtplib.SMTP_SSL(settings.smtp_host,settings.smtp_port,timeout=15,context=ssl.create_default_context()) as smtp:
                if settings.smtp_username:smtp.login(settings.smtp_username,settings.smtp_password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(settings.smtp_host,settings.smtp_port,timeout=15) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                if settings.smtp_username:smtp.login(settings.smtp_username,settings.smtp_password)
                smtp.send_message(message)
    except (OSError,smtplib.SMTPException) as exc:raise EmailDeliveryError("Email delivery failed") from exc
