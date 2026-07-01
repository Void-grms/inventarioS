import pytest


@pytest.fixture
def servicio(db):
    from inventario.models import Servicio
    return Servicio.objects.create(nombre="FARMACIA")


@pytest.fixture
def bien(db, servicio):
    from inventario.models import Bien
    return Bien.objects.create(
        codigo_patrimonial="462200500161",
        descripcion="ACUMULADOR DE ENERGIA",
        servicio=servicio,
        estado="Bueno",
        responsable="ESCOBEDO ALVARADO MODESTA",
    )
