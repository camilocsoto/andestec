# interface/adapters/alarm_adapters.py
import logging
import os
from typing import Optional, Dict, Any
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

logger = logging.getLogger(__name__)


class AlarmAdapters:
    """
    Envío de emails HTML a partir de plantilla.
    Requiere settings de email configurados (EMAIL_HOST, etc.) o usar tus variables .env mapeadas a settings.
    """

    def __init__(self) -> None:
        # Si usas .env directas, puedes leerlas aquí y setear settings dinámicamente si hace falta.
        self.from_email = getattr(settings, "EMAIL_HOST_USER", os.getenv("USER_MAIL", ""))

    def send_email_html(self, *, to_email: Optional[str], subject: str, context: Dict[str, Any]) -> None:
        logger.debug(f"Enviando email a {to_email} con subject: {subject}")
        if not to_email:
            logger.warning("No se proporcionó email de destino")
            return
        try:
            template = get_template("emails/alert_template.html")
            html_content = template.render(context)
            logger.debug("Template renderizado correctamente")

            message = EmailMultiAlternatives(
                subject=subject,
                body="",
                from_email=self.from_email,
                to=[to_email],
            )
            message.attach_alternative(html_content, "text/html")
            message.send()
            logger.info(f"Email enviado exitosamente a {to_email}")
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {e}", exc_info=True)
            # En producción: logger/Sentry
            pass
