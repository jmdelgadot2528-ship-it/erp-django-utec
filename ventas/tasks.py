# ventas/tasks.py
"""Tareas asíncronas de la app ventas — W17 (adaptada a PC escolar).

W17 implementa el envío de correos transaccionales. En la PC escolar
no hay salida de correo: el backend ArchivoEmailBackend guarda cada
mensaje en correos_enviados/ (.eml + .html). El código de las tareas es
el mismo que usaría un backend real (SendGrid, SMTP...): solo cambia
EMAIL_BACKEND en settings.

Idempotencia:
    Pedido.correo_enviado=True previene envíos duplicados si la tarea
    se llama más de una vez para el mismo pedido.
"""
import logging
from decimal import Decimal

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import F
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


def _items_con_subtotal(items) -> list:
    """Prepara las líneas del pedido para los templates de correo.

    Calcula el subtotal en Python con Decimal. (El filtro {% widthratio %}
    de la guía original redondea a entero: 3 × $99.50 daba $298, no $298.50.)

    Args:
        items: lista de dicts {nombre, precio (str), cantidad} o None.

    Returns:
        Lista de dicts con nombre, precio, cantidad y subtotal (Decimal).
    """
    resultado = []
    for item in items or []:
        precio   = Decimal(str(item.get('precio', '0')))
        cantidad = int(item.get('cantidad', 0))
        resultado.append({
            'nombre':   item.get('nombre', ''),
            'precio':   precio,
            'cantidad': cantidad,
            'subtotal': precio * cantidad,
        })
    return resultado


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='ventas.enviar_confirmacion_pedido',
)
def enviar_confirmacion_pedido(self, pedido_id: int) -> dict:
    """Envía el correo de confirmación de pedido al cliente.

    Garantías:
        - Idempotente: si correo_enviado=True, aborta sin error.
        - Reintenta hasta 3 veces si el backend de correo falla.

    Args:
        pedido_id: ID del Pedido confirmado.

    Returns:
        dict con estado, pedido_id y correo del destinatario.
    """
    from configuracion.models import ConfiguracionERP  # import local
    from ventas.models        import Pedido             # import local

    try:
        pedido = Pedido.objects.select_related('cliente').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(
            f'[correo_confirmacion] Pedido {pedido_id} no existe.'
        )
        return {'estado': 'error', 'razon': 'Pedido no encontrado'}

    # ── Verificación de idempotencia ────────────────────────────────────
    if pedido.correo_enviado:
        logger.info(
            f'[correo_confirmacion] Pedido {pedido.numero_pedido}: '
            f'correo ya enviado anteriormente — skip.'
        )
        return {
            'estado':    'skip',
            'pedido_id': pedido_id,
            'razon':     'correo ya enviado',
        }

    config = ConfiguracionERP.get_instance()

    # ── Contexto del correo ─────────────────────────────────────────────
    contexto = {
        'pedido':       pedido,
        'config':       config,
        'items':        _items_con_subtotal(pedido.items_snapshot),
        'url_catalogo': f'{settings.SITE_URL}/catalogo/',
    }

    # render_to_string sin request (las tareas no tienen request)
    asunto = (
        f'Confirmación de pedido {pedido.numero_pedido} '
        f'— {config.nombre_empresa}'
    )
    texto_plano = render_to_string('emails/confirmacion_pedido.txt', contexto)
    html_body   = render_to_string('emails/confirmacion_pedido.html', contexto)

    correo_destino = pedido.cliente.correo
    mensaje = EmailMultiAlternatives(
        subject    = asunto,
        body       = texto_plano,               # versión texto (fallback)
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [correo_destino],
    )
    mensaje.attach_alternative(html_body, 'text/html')

    # ── Enviar y manejar errores ────────────────────────────────────────
    try:
        mensaje.send()
        logger.info(
            f'[correo_confirmacion] Correo enviado a {correo_destino} '
            f'para pedido {pedido.numero_pedido}.'
        )

        # Marcar como enviado para evitar duplicados
        pedido.correo_enviado = True
        pedido.save(update_fields=['correo_enviado'])

        return {
            'estado':    'ok',
            'pedido_id': pedido_id,
            'correo':    correo_destino,
        }

    except Exception as exc:
        logger.error(
            f'[correo_confirmacion] Error al enviar correo para pedido '
            f'{pedido.numero_pedido}: {exc}'
        )
        # Reintento automático (hasta max_retries=3)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(
    bind=True,
    max_retries=1,
    name='ventas.verificar_stock_bajo',
)
def verificar_stock_bajo(self, umbral: int = 5) -> dict:
    """Verifica productos con stock bajo y envía alerta al admin.

    Args:
        umbral: cantidad mínima antes de alertar (default: 5).

    Returns:
        dict con conteo y lista de productos con stock bajo.
    """
    from productos.models import Producto   # import local

    productos_bajos = list(
        Producto.objects
        .filter(activo=True, stock__lt=umbral)
        .values('pk', 'nombre', 'stock',
                categoria_nombre=F('categoria__nombre'))
        .order_by('stock')
    )

    if not productos_bajos:
        logger.info(
            f'[stock_bajo] Todos los productos tienen stock >= {umbral}. OK.'
        )
        return {'umbral': umbral, 'total': 0, 'productos_bajos': []}

    logger.warning(
        f'[stock_bajo] {len(productos_bajos)} producto(s) con '
        f'stock < {umbral}.'
    )

    # Enviar alerta por correo si hay administradores configurados
    if settings.ADMINS:
        _enviar_alerta_stock(productos_bajos, umbral)

    return {
        'umbral':          umbral,
        'total':           len(productos_bajos),
        'productos_bajos': productos_bajos,
    }


def _enviar_alerta_stock(productos_bajos: list, umbral: int) -> None:
    """Envía el correo de alerta de stock al primer administrador.

    Args:
        productos_bajos: lista de dicts con nombre, stock y categoria_nombre.
        umbral:          umbral mínimo configurado.
    """
    from configuracion.models import ConfiguracionERP   # import local

    config = ConfiguracionERP.get_instance()

    contexto = {
        'productos_bajos': productos_bajos,
        'total_productos': len(productos_bajos),
        'umbral':          umbral,
        'fecha':           timezone.localtime().strftime('%d/%m/%Y %H:%M'),
        'url_admin':       f'{settings.SITE_URL}/admin/productos/producto/',
        'config':          config,
    }

    asunto = (
        f'[ALERTA] {len(productos_bajos)} producto(s) con stock < {umbral}'
    )
    texto_plano = render_to_string('emails/alerta_stock.txt',  contexto)
    html_body   = render_to_string('emails/alerta_stock.html', contexto)

    admin_nombre, admin_correo = settings.ADMINS[0]

    mensaje = EmailMultiAlternatives(
        subject    = asunto,
        body       = texto_plano,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [admin_correo],
    )
    mensaje.attach_alternative(html_body, 'text/html')

    try:
        mensaje.send()
        logger.info(
            f'[stock_bajo] Alerta enviada a {admin_correo}. '
            f'{len(productos_bajos)} productos.'
        )
    except Exception as exc:
        logger.error(f'[stock_bajo] Error al enviar alerta: {exc}')