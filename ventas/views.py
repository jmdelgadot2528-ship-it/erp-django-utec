# ventas/views.py
"""Vistas de la app ventas — W09 / W12.

Lectura: VentaListView y VentaDetailView.
Escritura y Borrado: crear_venta (con decoradores RBAC) y VentaDeleteView.
Exportación: venta_pdf (usando xhtml2pdf para entorno sin Docker).
"""
import io
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView

from xhtml2pdf import pisa

from configuracion.models import ConfiguracionERP
from .forms import DetalleVentaForm, VentaForm
from .models import DetalleVenta, Venta


class VentaListView(ListView):
    """Lista paginada de ventas en orden cronológico inverso."""

    model               = Venta
    template_name       = 'ventas/lista.html'
    context_object_name = 'ventas'
    paginate_by         = 20

    def get_queryset(self):
        """Pre-carga cliente para evitar N+1 en la tabla de ventas."""
        return (
            Venta.objects
            .select_related('cliente')
            .order_by('-fecha')
        )


class VentaDetailView(DetailView):
    """Detalle de una venta con todas sus líneas de producto."""

    model               = Venta
    template_name       = 'ventas/detalle.html'
    context_object_name = 'venta'
    pk_url_kwarg        = 'venta_id'

    def get_queryset(self):
        """Pre-carga cliente y prefetch líneas de detalle."""
        return (
            Venta.objects
            .select_related('cliente')
            .prefetch_related('detalles__producto')
        )


@login_required
@permission_required('ventas.add_venta', raise_exception=True)
def crear_venta(request):
    """Crea un encabezado de venta con una línea de detalle.

    Decoradores:
        @login_required            → verifica autenticación
        @permission_required(...)  → verifica permiso add_venta (403 si falla)
    """
    venta_form   = VentaForm(request.POST or None)
    detalle_form = DetalleVentaForm(request.POST or None)

    if request.method == 'POST':
        if venta_form.is_valid() and detalle_form.is_valid():
            venta         = venta_form.save()
            detalle       = detalle_form.save(commit=False)
            detalle.venta = venta
            detalle.save()
            messages.success(
                request,
                f'Venta #{venta.pk} registrada. Total: ${venta.total:.2f}'
            )
            return redirect('ventas:detalle', venta_id=venta.pk)

    return render(request, 'ventas/crear.html', {
        'venta_form':   venta_form,
        'detalle_form': detalle_form,
    })


class VentaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Confirmación y borrado de una venta con restricción por permiso."""

    model               = Venta
    template_name       = 'ventas/eliminar.html'
    pk_url_kwarg        = 'venta_id'
    success_url         = reverse_lazy('ventas:lista')
    permission_required = 'ventas.delete_venta'
    raise_exception     = True

    def form_valid(self, form):
        pk       = self.object.pk
        response = super().form_valid(form)
        messages.success(self.request, f'Venta #{pk} eliminada.')
        return response


import io
from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from configuracion.models import ConfiguracionERP
from .models import Venta


@login_required
def venta_pdf(request, venta_id: int) -> HttpResponse:
    """Genera y descarga la factura de una venta en formato PDF usando xhtml2pdf.

    Motor: xhtml2pdf (compatible con entornos sin Docker ni permisos de admin).

    Args:
        request:  HttpRequest de Django.
        venta_id: ID de la venta a generar.

    Returns:
        HttpResponse con Content-Type application/pdf y descarga directa.

    Raises:
        Http404: si la venta no existe.
    """
    venta = get_object_or_404(
        Venta.objects
        .select_related('cliente')
        .prefetch_related('detalles__producto__categoria'),
        pk=venta_id
    )

    config  = ConfiguracionERP.get_instance()
    context = {
        'venta':  venta,
        'config': config,
        'hoy':    date.today(),
    }

    html_string = render_to_string(
        'ventas/factura_pdf.html',
        context,
        request=request
    )

    # ── xhtml2pdf: conversión HTML → PDF sin Docker ───────────────────
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html_string, dest=buffer)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF con xhtml2pdf', status=500)

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="factura_{venta.pk:05d}.pdf"'
    )
    return response