import pytest
from openpyxl import Workbook
from django.core.management import call_command


HEADERS = [
    "codigo_patrimonial", "descripcion", "nombre_sede", "nombre_depend",
    "responsable", "usuario", "nombre_prov", "fecha_compra", "valor_compra",
    "fecha_alta", "valor_inicial", "sede", "pliego", "ubicac_fisica",
    "nombre_item", "sec_ejec", "tipo_modalidad", "codigo_barra", "modelo",
    "nro_orden", "medidas", "hvalor_neto", "abrev_movimto", "secuencia",
    "nro_documento", "flag_compartido", "nombre", "centro_costo", "nombre",
    "abreviatura", "fecha_nea", "tipo_doc_refer", "sec_modelo", "nro_serie",
    "grupo_bien", "clase_bien", "familia_bien", "item_bien", "color",
    "caracteristicas", "observaciones",
]


def _fila(codigo, ubic, estado, marca):
    fila = [""] * len(HEADERS)
    fila[0] = codigo
    fila[1] = "ACUMULADOR DE ENERGIA"
    fila[4] = "ESCOBEDO ALVARADO MODESTA"
    fila[10] = 339
    fila[13] = ubic          # ubicac_fisica
    fila[18] = "BV1000I"      # modelo
    fila[26] = marca         # AA nombre = marca
    fila[28] = estado        # AC nombre = estado
    fila[33] = "9B1935A12138"  # nro_serie
    fila[38] = "NEGRO"        # color
    return fila


@pytest.fixture
def excel_tmp(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.append(HEADERS)
    ws.append(_fila("462200500161", "FARMACIA", "Bueno", "APC"))
    ws.append(_fila("740805000054", "AUDITORIO", "Regular", "LENOVO"))
    ruta = tmp_path / "inv.xlsx"
    wb.save(ruta)
    return str(ruta)


def test_importar_crea_bienes_y_servicios(db, excel_tmp):
    from inventario.models import Bien, Servicio
    call_command("importar_excel", excel_tmp)
    assert Servicio.objects.count() == 2
    assert Bien.objects.count() == 2
    b = Bien.objects.get(codigo_patrimonial="462200500161")
    assert b.servicio.nombre == "FARMACIA"
    assert b.estado == "Bueno"
    assert b.marca == "APC"


def test_importar_es_idempotente(db, excel_tmp):
    from inventario.models import Bien
    call_command("importar_excel", excel_tmp)
    call_command("importar_excel", excel_tmp)
    assert Bien.objects.count() == 2
