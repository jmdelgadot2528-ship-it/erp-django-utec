# core/settings.py
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Variables de entorno ──────────────────────────────────────────────────
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / '.env', encoding = 'utf-8')

SECRET_KEY  = env('SECRET_KEY', default='dev-key-insegura-solo-para-desarrollo')
DEBUG = env('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['.onrender.com','localhost', '127.0.0.1'])

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
    # Terceros
    'rest_framework',
    'whitenoise.runserver_nostatic',
    # Apps del ERP
    'clientes',
    'proveedores',
    'productos',
    'ventas',
    'reportes',
    'configuracion',
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
]

ROOT_URLCONF = 'core.urls'

# ── Templates ─────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],       # carpeta global de templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
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

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Archivos media ────────────────────────────────────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Autenticación ─────────────────────────────────────────────────────────
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/'

# ── DRF ──────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
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


# core/settings.py — agregar al final del archivo

# ── JAZZMIN — Personalización del admin con Fable 5 AzulERP ───────────────
JAZZMIN_SETTINGS = {
    # Identidad
    'site_title':       'ERP Django',
    'site_header':      'ERP UTEC Celaya',
    'site_brand':       '📦 ERP Django',
    'welcome_sign':     'Bienvenido al Sistema ERP · UTEC Celaya',
    

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
    'custom_css':               'erp_custom.css',   # archivo en static/
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
    'navbar':                   'navbar-dark',
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
