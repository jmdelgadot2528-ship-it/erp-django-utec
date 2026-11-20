# core/correo_archivo.py
"""Backend de correo "a archivos" para PCs sin salida de correo — W17.

En lugar de enviar el mensaje por internet, guarda cada correo en la
carpeta EMAIL_FILE_PATH (por defecto: correos_enviados/ dentro del proyecto):

    20261118-171500-123456_confirmacion-de-pedido-ped-2026-0001.eml
    20261118-171500-123456_confirmacion-de-pedido-ped-2026-0001.html

    .eml  -> el correo completo (se abre con Outlook / Thunderbird / Correo)
    .html -> solo el cuerpo HTML (doble clic y se ve en el navegador)

Para el resto de Django funciona igual que cualquier backend:
send_mail(), EmailMultiAlternatives.send(), mail_admins()... no cambian.
"""
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.utils import timezone
from django.utils.text import slugify


class ArchivoEmailBackend(BaseEmailBackend):
    """Guarda cada correo como .eml (completo) y .html (vista previa)."""

    def __init__(self, *args, file_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        ruta = file_path or getattr(settings, 'EMAIL_FILE_PATH', None)
        if not ruta:
            raise ImproperlyConfigured(
                'Define EMAIL_FILE_PATH en settings.py para usar '
                'ArchivoEmailBackend.'
            )
        self.file_path = Path(ruta)

    def send_messages(self, email_messages):
        """Guarda los mensajes en disco. Devuelve cuántos guardó."""
        if not email_messages:
            return 0
        self.file_path.mkdir(parents=True, exist_ok=True)
        guardados = 0
        for mensaje in email_messages:
            try:
                self._guardar(mensaje)
            except Exception:
                if not self.fail_silently:
                    raise
            else:
                guardados += 1
        return guardados

    def _guardar(self, mensaje) -> None:
        """Escribe el .eml y, si existe, el .html del mensaje."""
        sello = timezone.localtime().strftime('%Y%m%d-%H%M%S-%f')
        asunto = slugify(mensaje.subject)[:50] or 'correo'
        base = f'{sello}_{asunto}'

        (self.file_path / f'{base}.eml').write_bytes(
            mensaje.message().as_bytes()
        )
        for contenido, mimetype in getattr(mensaje, 'alternatives', []):
            if mimetype == 'text/html':
                (self.file_path / f'{base}.html').write_text(
                    contenido, encoding='utf-8'
                )