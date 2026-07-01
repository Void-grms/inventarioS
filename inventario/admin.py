from django.contrib import admin

from .models import Bien, Foto, RegistroVerificacion, Servicio


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]


@admin.register(Bien)
class BienAdmin(admin.ModelAdmin):
    list_display = ["codigo_patrimonial", "descripcion", "servicio",
                    "estado", "responsable", "estado_verificacion"]
    list_filter = ["servicio", "estado_verificacion", "estado"]
    search_fields = ["codigo_patrimonial", "descripcion", "responsable"]


@admin.register(RegistroVerificacion)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ["bien", "verificador", "fecha", "cambios"]
    list_filter = ["verificador"]


admin.site.register(Foto)
