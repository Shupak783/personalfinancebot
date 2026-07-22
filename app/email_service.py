import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings


def send_html_email(subject: str, html_body: str, inline_images: dict[str, bytes] | None = None) -> None:
    """Sends an HTML email via SMTP using your own email account and an app password
    (never your real account password). Images are attached inline and referenced from
    html_body via cid: URIs, e.g. <img src="cid:category_chart">.
    """
    if not settings.email_username or not settings.email_app_password or not settings.email_to:
        raise RuntimeError(
            "Email is not configured. Set EMAIL_USERNAME, EMAIL_APP_PASSWORD, and EMAIL_TO in your .env."
        )

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = settings.email_from or settings.email_username
    msg["To"] = settings.email_to
    msg.attach(MIMEText(html_body, "html"))

    for cid, image_bytes in (inline_images or {}).items():
        image = MIMEImage(image_bytes)
        image.add_header("Content-ID", f"<{cid}>")
        image.add_header("Content-Disposition", "inline", filename=f"{cid}.png")
        msg.attach(image)

    with smtplib.SMTP(settings.email_smtp_host, settings.email_smtp_port) as server:
        server.starttls()
        server.login(settings.email_username, settings.email_app_password)
        server.sendmail(msg["From"], [settings.email_to], msg.as_string())
