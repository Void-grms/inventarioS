import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def usuario(db):
    return get_user_model().objects.create_user("juan", password="secreto")


def test_avance_requiere_login(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/login" in resp["Location"]


def test_avance_logueado_ok(client, usuario, bien):
    client.login(username="juan", password="secreto")
    resp = client.get("/")
    assert resp.status_code == 200
    # el nombre se muestra en title-case (Farmacia) por diseño
    assert b"Farmacia" in resp.content


def test_busqueda_por_codigo(client, usuario, bien):
    client.login(username="juan", password="secreto")
    resp = client.get("/buscar/?q=462200500161")
    assert resp.status_code == 200
    assert b"462200500161" in resp.content


def test_verificar_bien_por_post(client, usuario, bien):
    client.login(username="juan", password="secreto")
    resp = client.post(f"/bien/{bien.id}/", {
        "responsable": "NUEVO", "estado": "Bueno",
        "servicio": bien.servicio_id, "accion": "CONFORME",
        "observacion": "ok"})
    assert resp.status_code == 302
    bien.refresh_from_db()
    assert bien.estado_verificacion == "CONFORME"
    assert bien.responsable == "NUEVO"


def test_filtro_por_estado_en_servicio(client, usuario, servicio):
    from inventario.models import Bien
    Bien.objects.create(codigo_patrimonial="C1", descripcion="silla conforme",
                        servicio=servicio, estado="Bueno",
                        estado_verificacion="CONFORME")
    Bien.objects.create(codigo_patrimonial="F1", descripcion="mesa faltante",
                        servicio=servicio, estado="Bueno",
                        estado_verificacion="FALTANTE")
    client.login(username="juan", password="secreto")
    resp = client.get(f"/servicio/{servicio.id}/?estado=FALTANTE")
    assert resp.status_code == 200
    # los nombres se muestran en title-case por diseño
    assert b"Mesa Faltante" in resp.content
    assert b"Silla Conforme" not in resp.content


def test_ficha_muestra_observacion_guardada(client, usuario, bien):
    client.login(username="juan", password="secreto")
    client.post(f"/bien/{bien.id}/", {
        "responsable": "", "estado": "Bueno",
        "servicio": bien.servicio_id, "accion": "CAMBIADO",
        "observacion": "reubicado en almacen central"})
    resp = client.get(f"/bien/{bien.id}/")
    assert resp.status_code == 200
    assert b"reubicado en almacen central" in resp.content
