from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# valor almacenado -> (clase css, etiqueta legible)
_MAP = {
    "Pendiente": ("pendiente", "Pendiente"),
    "CONFORME": ("conforme", "Conforme"),
    "FALTANTE": ("faltante", "Faltante"),
    "CAMBIADO": ("cambiado", "Cambiado"),
    "DAÑADO": ("danado", "Dañado"),
}


@register.simple_tag
def estado_badge(valor):
    clase, etiqueta = _MAP.get(valor, ("pendiente", valor or "Pendiente"))
    return mark_safe(f'<span class="badge badge--{clase}">{etiqueta}</span>')


@register.filter
def clase_estado(valor):
    return _MAP.get(valor, ("pendiente", ""))[0]


_RESULTADOS = ("CONFORME", "FALTANTE", "CAMBIADO", "DAÑADO")


@register.filter
def corta_resultado(cambios):
    """Extrae el resultado (CONFORME/FALTANTE/…) del texto de 'cambios' de un registro."""
    texto = cambios or ""
    for r in _RESULTADOS:
        if r in texto:
            return r
    return "Pendiente"
