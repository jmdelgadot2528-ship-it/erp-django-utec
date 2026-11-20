# core/management/commands/probar_correo.py
"""Envía un correo de prueba y explica qué backend se usó y por qué falla.

Uso:
    python manage.py probar_correo tucorreo@gmail.com
"""
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Envía un correo de prueba y muestra el error real si falla.'

    def add_arguments(self, parser):
        parser.add_argument('destino', help='Correo que recibirá la prueba.')

    def handle(self, *args, **opciones):
        backend = settings.EMAIL_BACKEND
        self.stdout.write(f'Backend en uso : {backend}')
        self.stdout.write(f'Remitente      : {settings.DEFAULT_FROM_EMAIL}')
        if 'smtp' in backend:
            self.stdout.write(
                f'Servidor SMTP  : {settings.EMAIL_HOST}:{settings.EMAIL_PORT}'
                f' (usuario: {settings.EMAIL_HOST_USER or "SIN CONFIGURAR"})'
            )

        try:
            enviados = send_mail(
                subject='Prueba de correo — Catálogo',
                message='Si lees esto, el envío de correo funciona.',
                from_email=None,                      # usa DEFAULT_FROM_EMAIL
                recipient_list=[opciones['destino']],
                html_message='<h2>Prueba de correo — Catálogo</h2>'
                             '<p>Si lees esto, el envío funciona.</p>',
            )
        except Exception as exc:
            raise CommandError(
                f'FALLÓ el envío -> {type(exc).__name__}: {exc}'
            )

        self.stdout.write(self.style.SUCCESS(f'Mensajes enviados: {enviados}'))
        if 'console' in backend:
            self.stdout.write(
                'OJO: el backend es "console": el correo solo se imprimió '
                'arriba, NO sale a internet. Revisa EMAIL_MODE en .env.'
            )
        elif 'ArchivoEmailBackend' in backend:
            self.stdout.write(
                f'Modo archivo: abre la carpeta {settings.EMAIL_FILE_PATH} '
                f'(.html se ve en el navegador). No sale a internet.'
            )