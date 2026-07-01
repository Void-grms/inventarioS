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
    assert b"FARMACIA" in resp.content


def test_busqueda_por_codigo(client, usuario, bien):
    client.login(username="juan", password="secreto")
    resp = client.get("/buscar/?q=462200500161")
    assert resp.status_code == 200
    assert b"462200500161" in resp.content


def test_verificar_bien_por_post(client, usuario, bien):
    client.login(username="juan", password="secreto")
    resp = client.post(f"/bien/{bien.id}/", {
        "responsable": "NUEVO", "estado": "Bueno",
        "servicio": bien.servicio_id, "accion": "verificar",
        "observacion": "ok"})
    assert resp.status_code == 302
    bien.refresh_from_db()
    assert bien.estado_verificacion == "Verificado"
    assert bien.responsable == "NUEVO"
