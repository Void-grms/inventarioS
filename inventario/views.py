from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .exports import (bienes_por_responsable, bienes_por_servicio, exportar_excel)
from .forms import VerificacionForm
from .models import Bien, Servicio


@login_required
def avance(request):
    servicios = Servicio.objects.all()
    tarjetas = [{
        "obj": s, "total": s.total_bienes(),
        "verificados": s.total_verificados(),
        "faltantes": s.total_faltantes(),
    } for s in servicios]
    total = Bien.objects.count()
    verificados = Bien.objects.filter(estado_verificacion="Verificado").count()
    faltantes = Bien.objects.filter(estado_verificacion="Faltante").count()
    return render(request, "inventario/avance.html", {
        "tarjetas": tarjetas, "total": total,
        "verificados": verificados, "faltantes": faltantes,
    })


@login_required
def servicio_detalle(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    return render(request, "inventario/servicio_detalle.html", {
        "servicio": servicio, "bienes": servicio.bienes.all(),
    })


@login_required
def buscar(request):
    q = (request.GET.get("q") or "").strip()
    resultados = []
    if q:
        resultados = Bien.objects.filter(
            codigo_patrimonial__icontains=q) | Bien.objects.filter(
            descripcion__icontains=q)
        resultados = resultados.select_related("servicio").distinct()
    return render(request, "inventario/busqueda.html",
                {"q": q, "resultados": resultados})


@login_required
def bien_detalle(request, pk):
    bien = get_object_or_404(Bien, pk=pk)
    if request.method == "POST":
        form = VerificacionForm(request.POST, instance=bien)
        if form.is_valid():
            form.guardar(request.user)
            for archivo in request.FILES.getlist("fotos"):
                bien.fotos.create(imagen=archivo, tomada_por=request.user)
            return redirect("servicio_detalle", pk=bien.servicio_id)
    else:
        form = VerificacionForm(instance=bien)
    responsables = list(Bien.objects.exclude(responsable="")
                        .values_list("responsable", flat=True).distinct())
    return render(request, "inventario/bien_detalle.html", {
        "bien": bien, "form": form, "responsables": responsables,
    })


@login_required
def reporte_servicio(request):
    return render(request, "inventario/reporte_servicio.html",
                {"grupos": bienes_por_servicio()})


@login_required
def reporte_responsable(request):
    return render(request, "inventario/reporte_responsable.html",
                {"grupos": bienes_por_responsable()})


@login_required
def exportar(request):
    contenido = exportar_excel()
    resp = HttpResponse(
        contenido,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = 'attachment; filename="inventario_actualizado.xlsx"'
    return resp
