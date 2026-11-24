# core/settings.py
# ── Variables de entorno ──────────────────────────────────────────────────
import os
import environ
from pathlib import Path
from datetime import timedelta                    # si ya está arriba, no repetir
from celery.schedules import crontab              # lo usa CELERY_BEAT_SCHEDULE (W18)

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, True))

# Carga el archivo .env solo si existe (compatible con local y Render)
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file, encoding='utf-8')

SECRET_KEY    = env('SECRET_KEY', default='dev-key-insegura-solo-para-desarrollo')
DEBUG         = env('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['.onrender.com', 'localhost', '127.0.0.1'])
# ── Apps instaladas ───────────────────────────────────────────────────────
# core/settings.py — actualizar INSTALLED_APPS
INSTALLED_APPS = [
    # Jazzmin PRIMERO — antes de django.contrib.admin
    'jazzmin',                          # ← nueva línea, primera posición
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',        # ← requerido por allauth
    # Terceros
    'allauth',                     # ← nuevo
    'allauth.account',             # ← nuevo
    'allauth.socialaccount',       # ← nuevo (para OAuth futuro)
    'rest_framework',
    'anymail',
    'rest_framework.authtoken',
    'django_filters',
    'whitenoise.runserver_nostatic',
    # Apps del ERP
    'core',
    'clientes',
    'proveedores',
    'productos',
    'ventas',
    'reportes',
    'configuracion',
    'catalogo',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',   # ← agregar al final
]

ROOT_URLCONF = 'core.urls'

# ── Templates ─────────────────────────────────────────────────────────────
# core/settings.py — actualizar TEMPLATES[0]['OPTIONS']['context_processors']:
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Context processor del carrito — W13
                'catalogo.context_processors.carrito_info',
            ],
        },
    },
]

# ── Base de datos ─────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Internacionalización ──────────────────────────────────────────────────
LANGUAGE_CODE = 'es-mx'
TIME_ZONE     = 'America/Mexico_City'
USE_I18N      = True
USE_TZ        = True

# ── Archivos estáticos ────────────────────────────────────────────────────
# core/settings.py

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Agregar esta línea si no la tienes:
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Usa la versión no-manifiesto de WhiteNoise para evitar fallos si falta un archivo
# Reemplaza la línea de STATICFILES_STORAGE por esta:
STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedStaticFilesStorage'  # ← No falla si falta
                                                       # un archivo estático
)

# ── Archivos media ────────────────────────────────────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Autenticación ─────────────────────────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/productos/'
LOGOUT_REDIRECT_URL = '/'

# ── DRF ──────────────────────────────────────────────────────────────────
# core/settings.py — reemplazar la configuración REST_FRAMEWORK de W01:
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',   # para el navegador
        'rest_framework.authentication.TokenAuthentication',     # para clientes externos
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Seguridad de Cookies y Sesiones en Producción (Render) ────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True



# Permite las solicitudes CSRF desde tu dominio en Render
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://erp-django-utec-p2zz.onrender.com',
]


# ── STRIPE (Pasarela de pago) ──────────────────────────────────────────────
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

# core/settings.py — configuración de correo electrónico

# ── URL base (para los enlaces dentro de los correos) ─────────────────────
SITE_URL = env('SITE_URL', default='http://127.0.0.1:8000').rstrip('/')

# ── CELERY ────────────────────────────────────────────────────────────────
#   eager (por defecto): sin Redis ni worker; .delay() ejecuta la tarea ahí mismo.
#   redis              : cola real (casa / servidor con Redis). Requiere REDIS_URL.
CELERY_MODE = env('CELERY_MODE', default='eager')

CELERY_ACCEPT_CONTENT     = ['json']
CELERY_TASK_SERIALIZER    = 'json'
CELERY_RESULT_SERIALIZER  = 'json'
CELERY_TIMEZONE           = TIME_ZONE
CELERY_TASK_DEFAULT_QUEUE = 'erp_django'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_SOFT_TIME_LIMIT = 300
CELERY_TASK_TIME_LIMIT      = 360

if CELERY_MODE == 'redis':
    CELERY_BROKER_URL     = env('REDIS_URL', default='redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
    CELERY_TASK_ALWAYS_EAGER = False
else:
    CELERY_BROKER_URL     = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
    CELERY_TASK_ALWAYS_EAGER = True

# En eager, si una tarea falla NO tumba la vista web (se registra en el log).
# Los tests la activan con @override_settings(CELERY_TASK_EAGER_PROPAGATES=True).
CELERY_TASK_EAGER_PROPAGATES = False

# ── CORREO ELECTRÓNICO (W17) ──────────────────────────────────────────────
# En desarrollo: backend de consola (imprime el correo en la terminal).
# En producción: settings_prod.py activa anymail + SendGrid si existe
#                SENDGRID_API_KEY.
# En tests: Django usa SIEMPRE locmem (mail.outbox), sin importar esto.
EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)

# Remitente visible. En SendGrid DEBE ser un "Sender" verificado
# (Settings → Sender Authentication); si no, SendGrid responde 403.
DEFAULT_FROM_EMAIL = env(
    'DEFAULT_FROM_EMAIL',
    default='ERP Django <noreply@erp-django.com>'
)
# Remitente de los correos de error que Django envía a ADMINS
# (por defecto 'root@localhost', que SendGrid rechazaría).
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Prefijo SOLO para mail_admins()/mail_managers() (errores del sistema);
# no afecta a send_mail() ni a EmailMultiAlternatives.
EMAIL_SUBJECT_PREFIX = '[ERP Django] '

# Administradores que reciben alertas del sistema (stock bajo, errores 500)
ADMINS = [
    ('Admin ERP', env('ADMIN_EMAIL', default='admin@erp-django.com')),
]

# URL pública del sitio para los enlaces de los correos (las tareas
# Celery no tienen request → no hay build_absolute_uri()).
# Render define RENDER_EXTERNAL_URL automáticamente en cada servicio.
SITE_URL = env(
    'SITE_URL',
    default=env('RENDER_EXTERNAL_URL', default='http://127.0.0.1:8000')
).rstrip('/')

# django-anymail (SendGrid)
SENDGRID_API_KEY = env('SENDGRID_API_KEY', default='')
ANYMAIL = {
    'SENDGRID_API_KEY': SENDGRID_API_KEY,
}

# ── JAZZMIN — Personalización del admin con Fable 5 AzulERP ───────────────
JAZZMIN_SETTINGS = {
    # Identidad
    'site_title':       'Catálogo',
    'site_header':      'Catálogo',
    'site_brand':       '📦 Catálogo',
    'welcome_sign':     'Bienvenido a Catálogo',
    'copyright':        'Catálogo',
    

    # Icono del sitio (usar emoji como fallback)
    'site_icon':        None,
    'site_logo':        None,    # ruta a logo en static/ (agregar en W11+)

    # Búsqueda global en el admin
    'search_model':     ['clientes.Cliente', 'productos.Producto'],

    # Menú superior (top navigation)
    'topmenu_links': [
        {'name': 'Inicio ERP',   'url': '/', 'new_window': False},
        {'name': 'Productos',    'url': '/productos/'},
        {'name': 'Clientes',     'url': '/clientes/'},
        {'name': 'Ventas',       'url': '/ventas/'},
    ],

    # Menú de usuario (avatar)
    'usermenu_links': [
        {'name': 'Ver ERP', 'url': '/', 'new_window': False},
    ],

    # Menú lateral: orden de apps y modelos
    'order_with_respect_to': [
        'clientes', 'proveedores', 'productos',
        'ventas', 'configuracion', 'auth',
    ],

    # Iconos de Font Awesome para cada modelo
    'icons': {
        'auth':                       'fas fa-users-cog',
        'auth.user':                  'fas fa-user',
        'auth.Group':                 'fas fa-users',
        'clientes.Cliente':           'fas fa-user-tie',
        'proveedores.Proveedor':      'fas fa-truck',
        'productos.Categoria':        'fas fa-tags',
        'productos.Producto':         'fas fa-box',
        'ventas.Venta':               'fas fa-file-invoice-dollar',
        'ventas.DetalleVenta':        'fas fa-list',
        'ventas.Pedido':              'fas fa-shopping-cart',
        'configuracion.ConfiguracionERP': 'fas fa-cogs',
    },
    'default_icon_parents': 'fas fa-folder',
    'default_icon_children': 'fas fa-circle',

    # Apariencia
    'related_modal_active':     True,
    'custom_css':               None,   # archivo en static/
    'show_sidebar':             True,
    'navigation_expanded':      True,
    'hide_apps':                [],
    'hide_models':              [],

    # UI tweaks
    'changeform_format':        'horizontal_tabs',
    'language_chooser':         False,
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text':        False,
    'footer_small_text':        False,
    'body_small_text':          False,
    'brand_small_text':         False,
    'brand_colour':             'navbar-dark',
    'accent':                   'accent-navy',
    'navbar':                   'navbar-light',
    'no_navbar_border':         False,
    'navbar_fixed':             True,
    'layout_boxed':             False,
    'footer_fixed':             False,
    'sidebar_fixed':            True,
    'sidebar':                  'sidebar-dark-navy',
    'sidebar_nav_small_text':   False,
    'sidebar_disable_expand':   False,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style':   False,
    'theme':                    'default',
    'dark_mode_theme':          None,
    'button_classes': {
        'primary':   'btn-primary',
        'secondary': 'btn-secondary',
        'info':      'btn-info',
        'warning':   'btn-warning',
        'danger':    'btn-danger',
        'success':   'btn-success',
    },
}

# ── DJANGO SITES (requerido por allauth) ──────────────────────────────────
SITE_ID = 1

# ── AUTHENTICATION BACKENDS ───────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    # Backend estándar de Django (username + password en admin)
    'django.contrib.auth.backends.ModelBackend',
    # Backend de allauth (permite login por email también)
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ── ALLAUTH: configuración para desarrollo académico ──────────────────────
ACCOUNT_LOGIN_METHODS          = {'username'}   # login por username
ACCOUNT_EMAIL_REQUIRED         = False          # no obligar correo
ACCOUNT_EMAIL_VERIFICATION     = 'none'         # no enviar email de verificación
ACCOUNT_LOGOUT_ON_GET          = True           # logout sin confirmar (dev)
ACCOUNT_SESSION_REMEMBER       = True           # recordar sesión

# LOGIN_URL y LOGIN_REDIRECT_URL ya definidos en W01:
# LOGIN_URL           = '/accounts/login/'
# LOGIN_REDIRECT_URL  = '/productos/'
LOGOUT_REDIRECT_URL = '/'
