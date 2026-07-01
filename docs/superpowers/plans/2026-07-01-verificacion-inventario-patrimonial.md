# Sistema de Verificación de Inventario Patrimonial — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir una web app Django responsive para verificar en campo (desde el celular) los 385 bienes patrimoniales del C.S.M.C. Renacer Otuzco, asignar responsables, registrar estado/faltantes/fotos, y generar reportes, desplegada en Railway.

**Architecture:** Proyecto Django 5 con una sola app `inventario`. PostgreSQL como base de datos (SQLite en local para tests). Plantillas HTML mobile-first con Bootstrap 5. Importación desde el Excel existente mediante un management command. Fotos en volumen persistente. Multi-usuario con roles admin/verificador y bitácora de auditoría.

**Tech Stack:** Python 3.12, Django 5, PostgreSQL, gunicorn, whitenoise, openpyxl, dj-database-url, Pillow, Bootstrap 5, pytest-django.

**Repo destino:** https://github.com/Void-grms/inventarioS.git

---

## File Structure

```
inventarioS/
├── manage.py
├── requirements.txt
├── Procfile
├── railway.json
├── runtime.txt
├── .gitignore
├── .env.example
├── pytest.ini
├── config/                         # proyecto Django
│   ├── __init__.py
│   ├── settings.py                 # settings (env-driven)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── inventario/                     # app principal
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                   # Servicio, Bien, Foto, RegistroVerificacion
│   ├── admin.py                    # registro en panel /admin
│   ├── forms.py                    # formulario de verificación
│   ├── views.py                    # login, avance, servicio, búsqueda, ficha, reportes
│   ├── urls.py
│   ├── exports.py                  # exportación a Excel + reportes
│   ├── management/
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── importar_excel.py   # carga inicial del .xlsx
│   │       └── crear_admin.py      # crea superusuario admin desde env
│   ├── migrations/
│   ├── templates/inventario/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── avance.html
│   │   ├── servicio_detalle.html
│   │   ├── busqueda.html
│   │   ├── bien_detalle.html
│   │   ├── reporte_servicio.html
│   │   └── reporte_responsable.html
│   └── static/inventario/
│       └── app.css
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_importar_excel.py
│   ├── test_verificacion.py
│   ├── test_reportes.py
│   └── test_acceso.py
└── data/                           # (gitignored) fotos en local; en Railway = volumen /data
```

**Responsabilidades:**
- `config/settings.py` — configuración leída de variables de entorno (BD, secret, media, hosts).
- `inventario/models.py` — las 4 entidades del dominio.
- `inventario/views.py` — vistas de las pantallas de campo y reportes.
- `inventario/exports.py` — generación de Excel y agrupaciones para reportes (separado de views para poder testear puro).
- `management/commands/importar_excel.py` — parsea el Excel a la BD (idempotente por `codigo_patrimonial`).

---

## Task 1: Scaffolding del proyecto y dependencias

**Files:**
- Create: `requirements.txt`, `.gitignore`, `.env.example`, `pytest.ini`, `runtime.txt`
- Create: `manage.py`, `config/*`, `inventario/*` (vía `django-admin`)

- [ ] **Step 1: Crear entorno e instalar Django**

```bash
cd /c/Users/Usuario/Desktop/INVENTARIO
python -m venv .venv
source .venv/Scripts/activate
pip install "django>=5.0,<5.2" psycopg2-binary dj-database-url gunicorn whitenoise openpyxl Pillow pytest pytest-django
```

- [ ] **Step 2: Crear `requirements.txt`**

```
Django>=5.0,<5.2
psycopg2-binary>=2.9
dj-database-url>=2.1
gunicorn>=21.2
whitenoise>=6.6
openpyxl>=3.1
Pillow>=10.0
pytest>=8.0
pytest-django>=4.8
```

- [ ] **Step 3: Crear proyecto y app**

```bash
django-admin startproject config .
python manage.py startapp inventario
```

- [ ] **Step 4: Crear `.gitignore`**

```
.venv/
__pycache__/
*.pyc
db.sqlite3
.env
/data/
/staticfiles/
*.xlsx
!Inventario C.S.M.C. Renacer Otuzco 2025.xlsx
```

- [ ] **Step 5: Crear `runtime.txt`**

```
python-3.12
```

- [ ] **Step 6: Crear `.env.example`**

```
SECRET_KEY=cambia-esto-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
MEDIA_ROOT=./data
ADMIN_USERNAME=admin
ADMIN_PASSWORD=cambia-esto
```

- [ ] **Step 7: Crear `pytest.ini`**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
```

- [ ] **Step 8: Commit**

```bash
git init
git add .
git commit -m "chore: scaffolding inicial de Django y dependencias"
```

---

## Task 2: Configuración de settings (env-driven)

**Files:**
- Modify: `config/settings.py`

- [ ] **Step 1: Reemplazar bloques clave de `config/settings.py`**

```python
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-inseguro-cambiar")
DEBUG = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = [
    f"https://{h}" for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1")
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "inventario",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3"),
        conn_max_age=600,
    )
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", str(BASE_DIR / "data"))

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "avance"
LOGOUT_REDIRECT_URL = "login"

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

- [ ] **Step 2: Verificar que Django arranca**

Run: `python manage.py check`
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 3: Commit**

```bash
git add config/settings.py
git commit -m "feat: settings configurables por variables de entorno"
```

---

## Task 3: Modelos del dominio

**Files:**
- Modify: `inventario/models.py`
- Test: `tests/test_models.py`, `tests/conftest.py`

- [ ] **Step 1: Crear `tests/conftest.py`**

```python
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
```

- [ ] **Step 2: Escribir el test que falla `tests/test_models.py`**

```python
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
```

- [ ] **Step 3: Ejecutar el test para verlo fallar**

Run: `pytest tests/test_models.py -v`
Expected: FAIL (ImportError / modelos no existen)

- [ ] **Step 4: Implementar `inventario/models.py`**

```python
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
        return self.bienes.filter(estado_verificacion="Verificado").count()

    def total_faltantes(self):
        return self.bienes.filter(estado_verificacion="Faltante").count()


class Bien(models.Model):
    ESTADOS = [(e, e) for e in ("Bueno", "Regular", "Malo", "Nuevo")]
    ESTADOS_VERIF = [(e, e) for e in ("Pendiente", "Verificado", "Faltante")]

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
```

- [ ] **Step 5: Crear migraciones y correr tests**

Run: `python manage.py makemigrations inventario && pytest tests/test_models.py -v`
Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add inventario/models.py inventario/migrations tests/test_models.py tests/conftest.py
git commit -m "feat: modelos Servicio, Bien, Foto, RegistroVerificacion"
```

---

## Task 4: Importador del Excel

El Excel tiene encabezados en la fila 1. Columnas relevantes (por nombre de encabezado):
`codigo_patrimonial`, `descripcion`, `ubicac_fisica` (→ servicio), `responsable`,
`nombre` (col AC = estado Bueno/Regular/Malo), `nombre` (col AA = marca), `modelo`,
`nro_serie`, `color`, `medidas`, `caracteristicas`, `valor_inicial`, `fecha_alta`.
Nota: hay dos columnas con encabezado `nombre` (AA=marca, AC=estado); leer por índice de
columna, no solo por nombre, para desambiguar.

**Files:**
- Create: `inventario/management/__init__.py`, `inventario/management/commands/__init__.py`
- Create: `inventario/management/commands/importar_excel.py`
- Test: `tests/test_importar_excel.py`

- [ ] **Step 1: Crear los `__init__.py` de management/commands**

```bash
mkdir -p inventario/management/commands
touch inventario/management/__init__.py inventario/management/commands/__init__.py
```

- [ ] **Step 2: Escribir el test que falla `tests/test_importar_excel.py`**

```python
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
```

- [ ] **Step 3: Ejecutar el test para verlo fallar**

Run: `pytest tests/test_importar_excel.py -v`
Expected: FAIL (Unknown command 'importar_excel')

- [ ] **Step 4: Implementar `inventario/management/commands/importar_excel.py`**

```python
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand
from openpyxl import load_workbook

from inventario.models import Bien, Servicio

# Índices de columna (0-based) según el layout del Excel del inventario
COL = {
    "codigo": 0, "descripcion": 1, "responsable": 4, "valor": 10,
    "fecha_alta": 9, "ubicac": 13, "modelo": 18, "medidas": 20,
    "marca": 26, "estado": 28, "nro_serie": 33, "color": 38,
    "caracteristicas": 39,
}


def _txt(v):
    return "" if v is None else str(v).strip()


def _decimal(v):
    try:
        return Decimal(str(v))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _fecha(v):
    if isinstance(v, datetime):
        return v.date()
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(_txt(v), fmt).date()
        except ValueError:
            continue
    return None


class Command(BaseCommand):
    help = "Importa el inventario desde un archivo .xlsx"

    def add_arguments(self, parser):
        parser.add_argument("ruta", type=str)

    def handle(self, *args, **opts):
        wb = load_workbook(opts["ruta"], data_only=True)
        ws = wb.active
        creados, actualizados = 0, 0
        for fila in ws.iter_rows(min_row=2, values_only=True):
            codigo = _txt(fila[COL["codigo"]])
            if not codigo:
                continue
            nombre_serv = _txt(fila[COL["ubicac"]]) or "SIN UBICACION"
            servicio, _ = Servicio.objects.get_or_create(nombre=nombre_serv)
            estado = _txt(fila[COL["estado"]]) or "Regular"
            if estado not in dict(Bien.ESTADOS):
                estado = "Regular"
            defaults = dict(
                descripcion=_txt(fila[COL["descripcion"]]),
                servicio=servicio,
                estado=estado,
                responsable=_txt(fila[COL["responsable"]]),
                marca=_txt(fila[COL["marca"]]),
                modelo=_txt(fila[COL["modelo"]]),
                nro_serie=_txt(fila[COL["nro_serie"]]),
                color=_txt(fila[COL["color"]]),
                medidas=_txt(fila[COL["medidas"]]),
                caracteristicas=_txt(fila[COL["caracteristicas"]]),
                valor=_decimal(fila[COL["valor"]]),
                fecha_alta=_fecha(fila[COL["fecha_alta"]]),
            )
            _, creado = Bien.objects.update_or_create(
                codigo_patrimonial=codigo, defaults=defaults)
            creados += creado
            actualizados += not creado
        self.stdout.write(self.style.SUCCESS(
            f"Importados: {creados} nuevos, {actualizados} actualizados."))
```

- [ ] **Step 5: Correr los tests**

Run: `pytest tests/test_importar_excel.py -v`
Expected: PASS (2 tests)

- [ ] **Step 6: Probar con el Excel real e inspeccionar**

Run: `python manage.py migrate && python manage.py importar_excel "Inventario C.S.M.C. Renacer Otuzco 2025.xlsx"`
Expected: `Importados: 385 nuevos, 0 actualizados.`

- [ ] **Step 7: Commit**

```bash
git add inventario/management tests/test_importar_excel.py
git commit -m "feat: importador del inventario desde Excel"
```

---

## Task 5: Admin y comando crear_admin

**Files:**
- Modify: `inventario/admin.py`
- Create: `inventario/management/commands/crear_admin.py`

- [ ] **Step 1: Registrar modelos en `inventario/admin.py`**

```python
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
```

- [ ] **Step 2: Crear `inventario/management/commands/crear_admin.py`**

```python
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea (o actualiza) el superusuario admin desde variables de entorno"

    def handle(self, *args, **opts):
        User = get_user_model()
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD")
        if not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_PASSWORD no definido; se omite creación de admin."))
            return
        user, creado = User.objects.get_or_create(
            username=username, defaults={"is_staff": True, "is_superuser": True})
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        estado = "creado" if creado else "actualizado"
        self.stdout.write(self.style.SUCCESS(f"Admin '{username}' {estado}."))
```

- [ ] **Step 3: Verificar**

Run: `ADMIN_PASSWORD=test123 python manage.py crear_admin`
Expected: `Admin 'admin' creado.`

- [ ] **Step 4: Commit**

```bash
git add inventario/admin.py inventario/management/commands/crear_admin.py
git commit -m "feat: panel admin y comando crear_admin"
```

---

## Task 6: Formulario y lógica de verificación

**Files:**
- Create: `inventario/forms.py`
- Test: `tests/test_verificacion.py`

- [ ] **Step 1: Escribir el test que falla `tests/test_verificacion.py`**

```python
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
```

- [ ] **Step 2: Ejecutar el test para verlo fallar**

Run: `pytest tests/test_verificacion.py -v`
Expected: FAIL (ImportError VerificacionForm)

- [ ] **Step 3: Implementar `inventario/forms.py`**

```python
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
```

- [ ] **Step 4: Correr los tests**

Run: `pytest tests/test_verificacion.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add inventario/forms.py tests/test_verificacion.py
git commit -m "feat: formulario y logica de verificacion con bitacora"
```

---

## Task 7: Exportación a Excel y agrupaciones de reportes

**Files:**
- Create: `inventario/exports.py`
- Test: `tests/test_reportes.py`

- [ ] **Step 1: Escribir el test que falla `tests/test_reportes.py`**

```python
import pytest
from openpyxl import load_workbook

from inventario.exports import bienes_por_servicio, bienes_por_responsable, exportar_excel


@pytest.fixture
def datos(db):
    from inventario.models import Bien, Servicio
    s1 = Servicio.objects.create(nombre="FARMACIA")
    s2 = Servicio.objects.create(nombre="TRIAJE")
    Bien.objects.create(codigo_patrimonial="A1", descripcion="x", servicio=s1,
                        estado="Bueno", responsable="ANA")
    Bien.objects.create(codigo_patrimonial="A2", descripcion="y", servicio=s1,
                        estado="Bueno", responsable="LUIS")
    Bien.objects.create(codigo_patrimonial="A3", descripcion="z", servicio=s2,
                        estado="Bueno", responsable="ANA")
    return None


def test_agrupacion_por_servicio(datos):
    grupos = bienes_por_servicio()
    nombres = {g["servicio"]: len(g["bienes"]) for g in grupos}
    assert nombres["FARMACIA"] == 2
    assert nombres["TRIAJE"] == 1


def test_agrupacion_por_responsable(datos):
    grupos = bienes_por_responsable()
    nombres = {g["responsable"]: len(g["bienes"]) for g in grupos}
    assert nombres["ANA"] == 2
    assert nombres["LUIS"] == 1


def test_exportar_excel_devuelve_bytes(datos, tmp_path):
    contenido = exportar_excel()
    ruta = tmp_path / "out.xlsx"
    ruta.write_bytes(contenido)
    wb = load_workbook(ruta)
    ws = wb.active
    assert ws.cell(row=1, column=1).value == "codigo_patrimonial"
    assert ws.max_row == 4  # encabezado + 3 bienes
```

- [ ] **Step 2: Ejecutar el test para verlo fallar**

Run: `pytest tests/test_reportes.py -v`
Expected: FAIL (ImportError inventario.exports)

- [ ] **Step 3: Implementar `inventario/exports.py`**

```python
from io import BytesIO

from openpyxl import Workbook

from .models import Bien

COLUMNAS = [
    "codigo_patrimonial", "descripcion", "servicio", "estado", "responsable",
    "marca", "modelo", "nro_serie", "color", "medidas", "valor",
    "estado_verificacion", "verificado_por", "fecha_verificacion",
]


def _bienes_qs():
    return Bien.objects.select_related("servicio", "verificado_por").all()


def bienes_por_servicio():
    grupos = {}
    for b in _bienes_qs():
        grupos.setdefault(b.servicio.nombre, []).append(b)
    return [{"servicio": k, "bienes": grupos[k]} for k in sorted(grupos)]


def bienes_por_responsable():
    grupos = {}
    for b in _bienes_qs():
        clave = b.responsable or "(SIN RESPONSABLE)"
        grupos.setdefault(clave, []).append(b)
    return [{"responsable": k, "bienes": grupos[k]} for k in sorted(grupos)]


def exportar_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"
    ws.append(COLUMNAS)
    for b in _bienes_qs():
        ws.append([
            b.codigo_patrimonial, b.descripcion, b.servicio.nombre, b.estado,
            b.responsable, b.marca, b.modelo, b.nro_serie, b.color, b.medidas,
            float(b.valor) if b.valor is not None else "",
            b.estado_verificacion,
            b.verificado_por.username if b.verificado_por else "",
            b.fecha_verificacion.strftime("%Y-%m-%d %H:%M") if b.fecha_verificacion else "",
        ])
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
```

- [ ] **Step 4: Correr los tests**

Run: `pytest tests/test_reportes.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add inventario/exports.py tests/test_reportes.py
git commit -m "feat: exportacion a Excel y agrupaciones de reportes"
```

---

## Task 8: Vistas y URLs

**Files:**
- Modify: `inventario/views.py`, `config/urls.py`
- Create: `inventario/urls.py`
- Test: `tests/test_acceso.py`

- [ ] **Step 1: Escribir el test que falla `tests/test_acceso.py`**

```python
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
```

- [ ] **Step 2: Ejecutar el test para verlo fallar**

Run: `pytest tests/test_acceso.py -v`
Expected: FAIL (404 / vistas no existen)

- [ ] **Step 3: Implementar `inventario/views.py`**

```python
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .exports import (bienes_por_responsable, bienes_por_servicio, exportar_excel)
from .forms import VerificacionForm
from .models import Bien, Servicio


@login_required
def avance(request):
    servicios = Servicio.objects.all()
    tarjetas = [{
        "obj": s, "total": s.total_bienes(),
        "verificados": s.total_verificados(),
        "faltantes": s.total_faltantes(),
    } for s in servicios]
    total = Bien.objects.count()
    verificados = Bien.objects.filter(estado_verificacion="Verificado").count()
    faltantes = Bien.objects.filter(estado_verificacion="Faltante").count()
    return render(request, "inventario/avance.html", {
        "tarjetas": tarjetas, "total": total,
        "verificados": verificados, "faltantes": faltantes,
    })


@login_required
def servicio_detalle(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    return render(request, "inventario/servicio_detalle.html", {
        "servicio": servicio, "bienes": servicio.bienes.all(),
    })


@login_required
def buscar(request):
    q = (request.GET.get("q") or "").strip()
    resultados = []
    if q:
        resultados = Bien.objects.filter(
            codigo_patrimonial__icontains=q) | Bien.objects.filter(
            descripcion__icontains=q)
        resultados = resultados.select_related("servicio").distinct()
    return render(request, "inventario/busqueda.html",
                {"q": q, "resultados": resultados})


@login_required
def bien_detalle(request, pk):
    bien = get_object_or_404(Bien, pk=pk)
    if request.method == "POST":
        form = VerificacionForm(request.POST, instance=bien)
        if form.is_valid():
            form.guardar(request.user)
            for archivo in request.FILES.getlist("fotos"):
                bien.fotos.create(imagen=archivo, tomada_por=request.user)
            return redirect("servicio_detalle", pk=bien.servicio_id)
    else:
        form = VerificacionForm(instance=bien)
    responsables = list(Bien.objects.exclude(responsable="")
                        .values_list("responsable", flat=True).distinct())
    return render(request, "inventario/bien_detalle.html", {
        "bien": bien, "form": form, "responsables": responsables,
    })


@login_required
def reporte_servicio(request):
    return render(request, "inventario/reporte_servicio.html",
                {"grupos": bienes_por_servicio()})


@login_required
def reporte_responsable(request):
    return render(request, "inventario/reporte_responsable.html",
                {"grupos": bienes_por_responsable()})


@login_required
def exportar(request):
    contenido = exportar_excel()
    resp = HttpResponse(
        contenido,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = 'attachment; filename="inventario_actualizado.xlsx"'
    return resp
```

- [ ] **Step 4: Crear `inventario/urls.py`**

```python
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.avance, name="avance"),
    path("login/", auth_views.LoginView.as_view(
        template_name="inventario/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("buscar/", views.buscar, name="buscar"),
    path("servicio/<int:pk>/", views.servicio_detalle, name="servicio_detalle"),
    path("bien/<int:pk>/", views.bien_detalle, name="bien_detalle"),
    path("reportes/servicio/", views.reporte_servicio, name="reporte_servicio"),
    path("reportes/responsable/", views.reporte_responsable, name="reporte_responsable"),
    path("exportar/", views.exportar, name="exportar"),
]
```

- [ ] **Step 5: Actualizar `config/urls.py`**

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("inventario.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- [ ] **Step 6: Correr los tests**

Run: `pytest tests/test_acceso.py -v`
Expected: PASS (4 tests) — requiere que las plantillas de Task 9 existan; si fallan por
`TemplateDoesNotExist`, hacer Task 9 y volver a correr.

- [ ] **Step 7: Commit**

```bash
git add inventario/views.py inventario/urls.py config/urls.py tests/test_acceso.py
git commit -m "feat: vistas, urls y control de acceso"
```

---

## Task 9: Plantillas HTML (mobile-first, Bootstrap 5)

**Files:**
- Create: `inventario/templates/inventario/{base,login,avance,servicio_detalle,busqueda,bien_detalle,reporte_servicio,reporte_responsable}.html`
- Create: `inventario/static/inventario/app.css`

- [ ] **Step 1: `base.html`**

```html
{% load static %}
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Inventario Renacer Otuzco</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="{% static 'inventario/app.css' %}" rel="stylesheet">
</head>
<body class="bg-light">
<nav class="navbar navbar-dark bg-primary sticky-top">
  <div class="container-fluid">
    <a class="navbar-brand" href="{% url 'avance' %}">📋 Inventario</a>
    {% if user.is_authenticated %}
    <div class="d-flex gap-2">
      <a class="btn btn-sm btn-outline-light" href="{% url 'buscar' %}">🔍</a>
      <form method="post" action="{% url 'logout' %}" class="m-0">
        {% csrf_token %}
        <button class="btn btn-sm btn-outline-light">Salir</button>
      </form>
    </div>
    {% endif %}
  </div>
</nav>
<main class="container py-3">
  {% if messages %}
    {% for m in messages %}<div class="alert alert-info">{{ m }}</div>{% endfor %}
  {% endif %}
  {% block content %}{% endblock %}
</main>
</body>
</html>
```

- [ ] **Step 2: `login.html`**

```html
{% extends "inventario/base.html" %}
{% block content %}
<h1 class="h4 mb-3">Iniciar sesión</h1>
<form method="post">
  {% csrf_token %}
  <div class="mb-3">
    <label class="form-label">Usuario</label>
    <input name="username" class="form-control" autofocus required>
  </div>
  <div class="mb-3">
    <label class="form-label">Contraseña</label>
    <input name="password" type="password" class="form-control" required>
  </div>
  {% if form.errors %}<div class="alert alert-danger">Usuario o clave incorrectos.</div>{% endif %}
  <button class="btn btn-primary w-100">Entrar</button>
</form>
{% endblock %}
```

- [ ] **Step 3: `avance.html`**

```html
{% extends "inventario/base.html" %}
{% block content %}
<h1 class="h5 mb-3">Avance de verificación</h1>
<div class="row g-2 mb-3">
  <div class="col-4"><div class="card text-center"><div class="card-body p-2">
    <div class="h4 m-0">{{ total }}</div><small>Total</small></div></div></div>
  <div class="col-4"><div class="card text-center text-success"><div class="card-body p-2">
    <div class="h4 m-0">{{ verificados }}</div><small>Verificados</small></div></div></div>
  <div class="col-4"><div class="card text-center text-danger"><div class="card-body p-2">
    <div class="h4 m-0">{{ faltantes }}</div><small>Faltantes</small></div></div></div>
</div>
<form action="{% url 'buscar' %}" class="mb-3">
  <input name="q" class="form-control" placeholder="Buscar código o descripción...">
</form>
<div class="list-group">
  {% for t in tarjetas %}
  <a href="{% url 'servicio_detalle' t.obj.pk %}" class="list-group-item d-flex justify-content-between align-items-center">
    <span>{{ t.obj.nombre }}</span>
    <span class="badge bg-primary rounded-pill">{{ t.verificados }}/{{ t.total }}</span>
  </a>
  {% endfor %}
</div>
{% endblock %}
```

- [ ] **Step 4: `servicio_detalle.html`**

```html
{% extends "inventario/base.html" %}
{% block content %}
<h1 class="h5 mb-3">{{ servicio.nombre }}</h1>
<div class="list-group">
  {% for b in bienes %}
  <a href="{% url 'bien_detalle' b.pk %}" class="list-group-item">
    <div class="d-flex justify-content-between">
      <strong>{{ b.descripcion }}</strong>
      <span>
        {% if b.estado_verificacion == "Verificado" %}✅
        {% elif b.estado_verificacion == "Faltante" %}❌
        {% else %}⏳{% endif %}
      </span>
    </div>
    <small class="text-muted">{{ b.codigo_patrimonial }} · {{ b.responsable|default:"sin responsable" }}</small>
  </a>
  {% endfor %}
</div>
{% endblock %}
```

- [ ] **Step 5: `busqueda.html`**

```html
{% extends "inventario/base.html" %}
{% block content %}
<form class="mb-3">
  <input name="q" value="{{ q }}" class="form-control" placeholder="Buscar código o descripción..." autofocus>
</form>
<div class="list-group">
  {% for b in resultados %}
  <a href="{% url 'bien_detalle' b.pk %}" class="list-group-item">
    <strong>{{ b.descripcion }}</strong><br>
    <small class="text-muted">{{ b.codigo_patrimonial }} · {{ b.servicio.nombre }}</small>
  </a>
  {% empty %}
  {% if q %}<p class="text-muted">Sin resultados para "{{ q }}".</p>{% endif %}
  {% endfor %}
</div>
{% endblock %}
```

- [ ] **Step 6: `bien_detalle.html`**

```html
{% extends "inventario/base.html" %}
{% block content %}
<h1 class="h5">{{ bien.descripcion }}</h1>
<p class="text-muted mb-3">{{ bien.codigo_patrimonial }}</p>
<ul class="list-group mb-3">
  <li class="list-group-item"><small class="text-muted">Marca/Modelo</small><br>{{ bien.marca }} {{ bien.modelo }}</li>
  <li class="list-group-item"><small class="text-muted">Serie</small><br>{{ bien.nro_serie|default:"—" }}</li>
  <li class="list-group-item"><small class="text-muted">Estado verificación</small><br>{{ bien.estado_verificacion }}</li>
</ul>

<form method="post" enctype="multipart/form-data">
  {% csrf_token %}
  <div class="mb-3">
    <label class="form-label">Responsable</label>
    <input name="responsable" list="responsables" value="{{ bien.responsable }}" class="form-control">
    <datalist id="responsables">
      {% for r in responsables %}<option value="{{ r }}">{% endfor %}
    </datalist>
  </div>
  <div class="mb-3">
    <label class="form-label">Estado</label>
    <select name="estado" class="form-select">
      {% for val, txt in form.fields.estado.choices %}
      <option value="{{ val }}" {% if bien.estado == val %}selected{% endif %}>{{ txt }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="mb-3">
    <label class="form-label">Servicio / Ubicación</label>
    <select name="servicio" class="form-select">
      {% for s in form.fields.servicio.queryset %}
      <option value="{{ s.pk }}" {% if bien.servicio_id == s.pk %}selected{% endif %}>{{ s.nombre }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="mb-3">
    <label class="form-label">Foto</label>
    <input type="file" name="fotos" accept="image/*" capture="environment" class="form-control" multiple>
  </div>
  <div class="mb-3">
    <label class="form-label">Observación</label>
    <textarea name="observacion" class="form-control" rows="2"></textarea>
  </div>
  <div class="d-grid gap-2">
    <button name="accion" value="verificar" class="btn btn-success">✅ Guardar verificación</button>
    <button name="accion" value="faltante" class="btn btn-outline-danger">❌ Marcar como faltante</button>
  </div>
</form>

{% if bien.fotos.all %}
<div class="mt-3 row g-2">
  {% for f in bien.fotos.all %}<div class="col-4"><img src="{{ f.imagen.url }}" class="img-fluid rounded"></div>{% endfor %}
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 7: `reporte_servicio.html`**

```html
{% extends "inventario/base.html" %}
{% block content %}
<div class="d-flex justify-content-between mb-3">
  <h1 class="h5">Reporte por servicio</h1>
  <a class="btn btn-sm btn-success" href="{% url 'exportar' %}">⬇ Excel</a>
</div>
{% for g in grupos %}
<h2 class="h6 mt-3">{{ g.servicio }}</h2>
<table class="table table-sm">
  <thead><tr><th>Código</th><th>Descripción</th><th>Responsable</th></tr></thead>
  <tbody>
    {% for b in g.bienes %}
    <tr><td>{{ b.codigo_patrimonial }}</td><td>{{ b.descripcion }}</td><td>{{ b.responsable }}</td></tr>
    {% endfor %}
  </tbody>
</table>
{% endfor %}
{% endblock %}
```

- [ ] **Step 8: `reporte_responsable.html`**

```html
{% extends "inventario/base.html" %}
{% block content %}
<div class="d-flex justify-content-between mb-3">
  <h1 class="h5">Reporte por responsable</h1>
  <a class="btn btn-sm btn-success" href="{% url 'exportar' %}">⬇ Excel</a>
</div>
{% for g in grupos %}
<h2 class="h6 mt-3">{{ g.responsable }}</h2>
<table class="table table-sm">
  <thead><tr><th>Código</th><th>Descripción</th><th>Servicio</th></tr></thead>
  <tbody>
    {% for b in g.bienes %}
    <tr><td>{{ b.codigo_patrimonial }}</td><td>{{ b.descripcion }}</td><td>{{ b.servicio.nombre }}</td></tr>
    {% endfor %}
  </tbody>
</table>
{% endfor %}
{% endblock %}
```

- [ ] **Step 9: `static/inventario/app.css`**

```css
body { -webkit-text-size-adjust: 100%; }
.list-group-item strong { font-size: 0.95rem; }
main { max-width: 640px; }
```

- [ ] **Step 10: Correr toda la suite**

Run: `pytest -v`
Expected: PASS (todos los tests, incluidos los de Task 8)

- [ ] **Step 11: Commit**

```bash
git add inventario/templates inventario/static
git commit -m "feat: plantillas mobile-first con Bootstrap"
```

---

## Task 10: Archivos de despliegue en Railway

**Files:**
- Create: `Procfile`, `railway.json`

- [ ] **Step 1: Crear `Procfile`**

```
web: gunicorn config.wsgi --bind 0.0.0.0:$PORT
release: python manage.py migrate --noinput && python manage.py crear_admin && python manage.py collectstatic --noinput
```

- [ ] **Step 2: Crear `railway.json`**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": { "builder": "NIXPACKS" },
  "deploy": {
    "startCommand": "gunicorn config.wsgi --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

- [ ] **Step 3: Verificar collectstatic en local**

Run: `python manage.py collectstatic --noinput`
Expected: archivos copiados a `staticfiles/` sin errores.

- [ ] **Step 4: Commit**

```bash
git add Procfile railway.json
git commit -m "chore: archivos de despliegue para Railway"
```

---

## Task 11: README con pasos de despliegue

**Files:**
- Create: `README.md`

- [ ] **Step 1: Crear `README.md`**

````markdown
# Sistema de Verificación de Inventario Patrimonial — C.S.M.C. Renacer Otuzco

Web app Django para verificar bienes patrimoniales desde el celular, asignar
responsables y generar reportes.

## Desarrollo local

```bash
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
ADMIN_PASSWORD=admin123 python manage.py crear_admin
python manage.py importar_excel "Inventario C.S.M.C. Renacer Otuzco 2025.xlsx"
python manage.py runserver
```

Abrir http://127.0.0.1:8000 · usuario `admin`.

## Pruebas

```bash
pytest -v
```

## Despliegue en Railway

1. Subir el repo a GitHub: https://github.com/Void-grms/inventarioS.git
2. En Railway: **New Project → Deploy from GitHub repo**.
3. Añadir plugin **PostgreSQL** (crea `DATABASE_URL` automáticamente).
4. Añadir un **Volume** montado en `/data`.
5. Variables de entorno:
   - `SECRET_KEY` (aleatorio largo)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=<tu-subdominio>.up.railway.app`
   - `MEDIA_ROOT=/data`
   - `ADMIN_USERNAME=admin`
   - `ADMIN_PASSWORD=<clave segura>`
6. El comando `release` corre migraciones, crea el admin y junta estáticos.
7. Cargar el inventario una vez desde la consola de Railway:
   `python manage.py importar_excel "Inventario C.S.M.C. Renacer Otuzco 2025.xlsx"`
   (o subir el Excel al repo para que esté disponible en el contenedor).
````

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README con desarrollo y despliegue en Railway"
```

- [ ] **Step 3: Conectar el remote y publicar**

```bash
git remote add origin https://github.com/Void-grms/inventarioS.git
git branch -M main
git push -u origin main
```

---

## Notas de verificación final

Tras completar todas las tareas:
- `pytest -v` → toda la suite en verde.
- `python manage.py runserver` y probar el flujo en el navegador del celular
  (misma red, o desplegado en Railway): login → avance → servicio → ficha →
  guardar verificación → foto → reportes → exportar Excel.
- Confirmar en Railway que el volumen `/data` conserva las fotos tras un redeploy.
```
