# notifications/infrastructure/email_sender.py
import smtplib
import logging
import re
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.config import settings
from notifications.infrastructure.templates.template_renderer import TemplateRenderer, template_renderer

logger = logging.getLogger(__name__)


class AbstractEmailSender(ABC):

    @abstractmethod
    def send_plain(self, to: str, subject: str, body: str) -> None:
        ...

    @abstractmethod
    def send_multipart(self, to: str, subject: str, html_body: str, text_body: str | None = None) -> None:
        ...

    @abstractmethod
    def send_template(self, to: str, subject: str, template_name: str, context: dict) -> None:
        ...


class SMTPEmailSender(AbstractEmailSender):

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_email: str,
        renderer: TemplateRenderer,
        use_tls: bool = True,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_email = from_email
        self._renderer = renderer
        self._use_tls = use_tls

    def send_plain(self, to: str, subject: str, body: str) -> None:
        message = self._build_plain_message(to, subject, body)
        self._dispatch(to, message)

    def send_multipart(self, to: str, subject: str, html_body: str, text_body: str | None = None) -> None:
        message = self._build_multipart_message(to, subject, html_body, text_body)
        self._dispatch(to, message)

    def send_template(self, to: str, subject: str, template_name: str, context: dict) -> None:
        html_body = self._renderer.render(template_name, **context)
        text_body = self._strip_html(html_body)
        self.send_multipart(to=to, subject=subject, html_body=html_body, text_body=text_body)

    def _strip_html(self, html: str) -> str:
        # crude fallback plain-text — good enough for the alt-view most clients never show
        text = re.sub(r"<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", text).strip()

    def _build_plain_message(self, to: str, subject: str, body: str) -> MIMEText:
        message = MIMEText(body, "plain")
        message["Subject"] = subject
        message["From"] = self._from_email
        message["To"] = to
        return message

    def _build_multipart_message(
        self, to: str, subject: str, html_body: str, text_body: str | None
    ) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self._from_email
        message["To"] = to

        if text_body:
            message.attach(MIMEText(text_body, "plain"))
        message.attach(MIMEText(html_body, "html"))

        return message

    def _dispatch(self, to: str, message: MIMEText | MIMEMultipart) -> None:
        try:
            with smtplib.SMTP(self._host, self._port, timeout=10) as server:
                if self._use_tls:
                    server.starttls()
                server.login(self._username, self._password)
                server.sendmail(self._from_email, [to], message.as_string())
        except smtplib.SMTPException:
            logger.exception("Failed to send email to %s", to)
            raise


email_sender = SMTPEmailSender(
    host=settings.EMAIL_HOST,
    port=settings.EMAIL_PORT,
    username=settings.EMAIL_HOST_USER,
    password=settings.EMAIL_HOST_PASSWORD,
    from_email=settings.EMAIL_FROM,
    renderer=template_renderer,
    use_tls=settings.EMAIL_USE_TLS,
)