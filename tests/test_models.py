import pytest


def test_bien_defaults_a_pendiente(bien):
    assert bien.estado_verificacion == "Pendiente"
    assert bien.fecha_verificacion is None
    assert bien.verificado_por is None


def test_str_bien(bien):
    assert "462200500161" in str(bien)


def test_servicio_progreso(db, servicio):
    from inventario.models import Bien
    Bien.objects.create(codigo_patrimonial="A1", descripcion="x",
                        servicio=servicio, estado="Bueno",
                        estado_verificacion="Verificado")
    Bien.objects.create(codigo_patrimonial="A2", descripcion="y",
                        servicio=servicio, estado="Bueno")
    assert servicio.total_bienes() == 2
    assert servicio.total_verificados() == 1
