from django.conf import settings
from django.db import models


class Servicio(models.Model):
    nombre = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def total_bienes(self):
        return self.bienes.count()

    def total_verificados(self):
        return self.bienes.exclude(estado_verificacion="Pendiente").count()

    def total_faltantes(self):
        return self.bienes.filter(estado_verificacion="FALTANTE").count()


class Bien(models.Model):
    ESTADOS = [(e, e) for e in ("Bueno", "Regular", "Malo", "Nuevo")]
    # Estado de verificación: 'Pendiente' (aún no revisado) + 4 resultados posibles.
    RESULTADOS = ("CONFORME", "FALTANTE", "CAMBIADO", "DAÑADO")
    ESTADOS_VERIF = [
        ("Pendiente", "Pendiente"),
        ("CONFORME", "Conforme"),
        ("FALTANTE", "Faltante"),
        ("CAMBIADO", "Cambiado"),
        ("DAÑADO", "Dañado"),
    ]

    codigo_patrimonial = models.CharField(max_length=30, unique=True, db_index=True)
    descripcion = models.CharField(max_length=300)
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name="bienes")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="Regular")
    responsable = models.CharField(max_length=200, blank=True)

    marca = models.CharField(max_length=200, blank=True)
    modelo = models.CharField(max_length=200, blank=True)
    nro_serie = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=100, blank=True)
    medidas = models.CharField(max_length=100, blank=True)
    caracteristicas = models.CharField(max_length=500, blank=True)
    valor = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha_alta = models.DateField(null=True, blank=True)
    datos_extra = models.JSONField(default=dict, blank=True)

    estado_verificacion = models.CharField(
        max_length=20, choices=ESTADOS_VERIF, default="Pendiente")
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    verificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="bienes_verificados")

    class Meta:
        ordering = ["codigo_patrimonial"]

    def __str__(self):
        return f"{self.codigo_patrimonial} - {self.descripcion}"


class Foto(models.Model):
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name="fotos")
    imagen = models.ImageField(upload_to="fotos/")
    tomada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.bien.codigo_patrimonial}"


class RegistroVerificacion(models.Model):
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name="registros")
    verificador = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    fecha = models.DateTimeField(auto_now_add=True)
    cambios = models.CharField(max_length=500, blank=True)
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Registro {self.bien.codigo_patrimonial} @ {self.fecha:%Y-%m-%d %H:%M}"
