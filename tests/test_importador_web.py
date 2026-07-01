import io

import pytest
from django.contrib.auth import get_user_model
from openpyxl import Workbook

from inventario.importador import importar_inventario

# Reutilizamos el layout de encabezados del test del comando
from tests.test_importar_excel import HEADERS, _fila


@pytest.fixture
def excel_bytes():
    wb = Workbook()
    ws = wb.active
    ws.append(HEADERS)
    ws.append(_fila("462200500161", "FARMACIA", "Bueno", "APC"))
    ws.append(_fila("740805000054", "AUDITORIO", "Regular", "LENOVO"))
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_user(
        "jefe", password="secreto", is_staff=True, is_superuser=True)


@pytest.fixture
def normal_user(db):
    return get_user_model().objects.create_user("juan", password="secreto")


def test_importar_inventario_desde_filelike(db, excel_bytes):
    from inventario.models import Bien, Servicio
    creados, actualizados = importar_inventario(excel_bytes)
    assert creados == 2
    assert actualizados == 0
    assert Servicio.objects.count() == 2
    assert Bien.objects.get(codigo_patrimonial="462200500161").marca == "APC"


def test_vista_importar_requiere_admin(client, normal_user):
    client.login(username="juan", password="secreto")
    resp = client.get("/importar/")
    # un usuario sin permisos de staff no debe acceder
    assert resp.status_code in (302, 403)


def test_vista_importar_admin_sube_excel(client, admin_user, excel_bytes):
    from django.core.files.uploadedfile import SimpleUploadedFile
    from inventario.models import Bien
    client.login(username="jefe", password="secreto")
    archivo = SimpleUploadedFile(
        "inv.xlsx", excel_bytes.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp = client.post("/importar/", {"archivo": archivo})
    assert resp.status_code == 302
    assert Bien.objects.count() == 2
