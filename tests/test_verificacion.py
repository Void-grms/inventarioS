import pytest
from django.contrib.auth import get_user_model

from inventario.forms import VerificacionForm


@pytest.fixture
def usuario(db):
    return get_user_model().objects.create_user("juan", password="x")


def test_form_guarda_y_marca_verificado(bien, usuario):
    form = VerificacionForm(
        data={"responsable": "NUEVO RESPONSABLE", "estado": "Regular",
              "servicio": bien.servicio_id, "accion": "verificar",
              "observacion": "todo ok"},
        instance=bien)
    assert form.is_valid(), form.errors
    form.guardar(usuario)
    bien.refresh_from_db()
    assert bien.responsable == "NUEVO RESPONSABLE"
    assert bien.estado_verificacion == "Verificado"
    assert bien.verificado_por == usuario
    assert bien.fecha_verificacion is not None
    assert bien.registros.count() == 1


def test_form_marca_faltante(bien, usuario):
    form = VerificacionForm(
        data={"responsable": "", "estado": "Regular",
              "servicio": bien.servicio_id, "accion": "faltante",
              "observacion": "no se encontro"},
        instance=bien)
    assert form.is_valid(), form.errors
    form.guardar(usuario)
    bien.refresh_from_db()
    assert bien.estado_verificacion == "Faltante"
    assert bien.registros.count() == 1
