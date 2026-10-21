# productos/views.py
"""Vistas de la app productos — W09.

Lectura: ProductoListView y ProductoDetailView.
Escritura: ProductoCreateView, ProductoUpdateView y ProductoDeleteView.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import ProductoForm
from .models import Producto


class ProductoListView(ListView):
    """Lista paginada de productos."""

    model               = Producto
    template_name       = 'productos/lista.html'
    context_object_name = 'productos'
    paginate_by         = 20

    def get_queryset(self):
        return (
            Producto.objects
            .select_related('categoria')
            .order_by('nombre')
        )


class ProductoDetailView(DetailView):
    """Detalle de un producto específico."""

    model               = Producto
    template_name       = 'productos/detalle.html'
    context_object_name = 'producto'
    pk_url_kwarg        = 'producto_id'


class ProductoCreateView(LoginRequiredMixin, CreateView):
    """Formulario para crear un nuevo producto."""

    model         = Producto
    form_class    = ProductoForm
    template_name = 'productos/crear.html'
    success_url   = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Producto "{self.object.nombre}" creado exitosamente.'
        )
        return response


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    """Formulario para editar un producto."""

    model         = Producto
    form_class    = ProductoForm
    template_name = 'productos/editar.html'
    pk_url_kwarg  = 'producto_id'
    success_url   = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Producto "{self.object.nombre}" actualizado.'
        )
        return response


class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Confirmación y borrado de un producto (Requiere permiso delete_producto)."""

    model               = Producto
    template_name       = 'productos/eliminar.html'
    pk_url_kwarg        = 'producto_id'
    success_url         = reverse_lazy('productos:lista')
    permission_required = 'productos.delete_producto'

    def handle_no_permission(self):
        # Si el usuario NO está autenticado -> redirige al login (302)
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        # Si SÍ está autenticado pero no tiene permiso -> Lanza HTTP 403 Forbidden
        return super().handle_no_permission()

    def form_valid(self, form):
        nombre   = self.object.nombre
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{nombre}" eliminado.')
        return response