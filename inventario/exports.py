from io import BytesIO

from openpyxl import Workbook

from .models import Bien

COLUMNAS = [
    "codigo_patrimonial", "descripcion", "servicio", "estado", "responsable",
    "marca", "modelo", "nro_serie", "color", "medidas", "valor",
    "estado_verificacion", "verificado_por", "fecha_verificacion",
]


def _bienes_qs():
    return Bien.objects.select_related("servicio", "verificado_por").all()


def bienes_por_servicio():
    grupos = {}
    for b in _bienes_qs():
        grupos.setdefault(b.servicio.nombre, []).append(b)
    return [{"servicio": k, "bienes": grupos[k]} for k in sorted(grupos)]


def bienes_por_responsable():
    grupos = {}
    for b in _bienes_qs():
        clave = b.responsable or "(SIN RESPONSABLE)"
        grupos.setdefault(clave, []).append(b)
    return [{"responsable": k, "bienes": grupos[k]} for k in sorted(grupos)]


def exportar_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"
    ws.append(COLUMNAS)
    for b in _bienes_qs():
        ws.append([
            b.codigo_patrimonial, b.descripcion, b.servicio.nombre, b.estado,
            b.responsable, b.marca, b.modelo, b.nro_serie, b.color, b.medidas,
            float(b.valor) if b.valor is not None else "",
            b.estado_verificacion,
            b.verificado_por.username if b.verificado_por else "",
            b.fecha_verificacion.strftime("%Y-%m-%d %H:%M") if b.fecha_verificacion else "",
        ])
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
