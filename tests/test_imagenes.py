import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def _imagen_grande(ancho=3200, alto=2400):
    """Genera un JPEG grande simulando una foto de celular."""
    img = Image.new("RGB", (ancho, alto), (120, 140, 160))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


def test_comprimir_reduce_dimension_y_peso():
    from inventario.imagenes import comprimir_imagen
    original = _imagen_grande()
    archivo = SimpleUploadedFile("foto.jpg", original, content_type="image/jpeg")
    content = comprimir_imagen(archivo)
    img = Image.open(content)
    assert max(img.size) <= 1600
    assert content.size < len(original)


def test_foto_se_comprime_al_guardar(db, bien, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    from inventario.models import Foto
    archivo = SimpleUploadedFile("camara.png", _imagen_grande(), content_type="image/png")
    foto = Foto.objects.create(bien=bien, imagen=archivo)
    foto.refresh_from_db()
    assert foto.imagen.name.endswith(".jpg")
    img = Image.open(foto.imagen.path)
    assert max(img.size) <= 1600
