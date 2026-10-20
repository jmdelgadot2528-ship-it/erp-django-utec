# core/views.py
from django.shortcuts import render
from django.urls import reverse


def bienvenida(request):
    modulos = [
        {
            'nombre': 'Productos',
            'icono': '📦',
            'url': reverse('productos:lista'),  # ← Cambiar a 'lista'
            'descripcion': 'Inventario, precios y stock',
        },
        {
            'nombre': 'Clientes',
            'icono': '👥',
            'url': reverse('clientes:lista'),  # ← Cambiar a 'lista'
            'descripcion': 'Cartera y gestión de clientes',
        },
        {
            'nombre': 'Proveedores',
            'icono': '🏭',
            'url': reverse('proveedores:lista'),  # ← Cambiar a 'lista'
            'descripcion': 'Red de proveedores',
        },
        {
            'nombre': 'Ventas',
            'icono': '💰',
            'url': reverse('ventas:lista'),  # ← Cambiar a 'lista'
            'descripcion': 'Pedidos, facturas y cobros',
        },
        {
            'nombre': 'Reportes',
            'icono': '📊',
            'url': reverse('reportes:inicio'),
            'descripcion': 'Dashboard y analítica',
        },
        {
            'nombre': 'Admin',
            'icono': '⚙️',
            'url': '/admin/',
            'descripcion': 'Panel de administración Django',
        },
    ]
    return render(request, 'bienvenida.html', {'modulos': modulos})