from django.forms import ModelForm
from django.utils import timezone

from .models import Bien, RegistroVerificacion


class VerificacionForm(ModelForm):
    class Meta:
        model = Bien
        fields = ["responsable", "estado", "servicio"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 'accion' y 'observacion' no son campos del modelo; se leen de data
        self.accion = (self.data.get("accion") or "verificar").strip()
        self.observacion = (self.data.get("observacion") or "").strip()

    def guardar(self, usuario):
        bien = self.save(commit=False)
        cambios = []
        if "responsable" in self.changed_data:
            cambios.append("responsable")
        if "estado" in self.changed_data:
            cambios.append("estado")
        if "servicio" in self.changed_data:
            cambios.append("ubicacion")
        if self.accion == "faltante":
            bien.estado_verificacion = "Faltante"
            cambios.append("faltante")
        else:
            bien.estado_verificacion = "Verificado"
        bien.fecha_verificacion = timezone.now()
        bien.verificado_por = usuario
        bien.save()
        RegistroVerificacion.objects.create(
            bien=bien, verificador=usuario,
            cambios=", ".join(cambios), observacion=self.observacion)
        return bien
