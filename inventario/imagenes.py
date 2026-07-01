"""Compresión de imágenes tomadas desde el celular.

Reduce el lado mayor y recodifica a JPEG para que las fotos de la cámara
(que suelen pesar varios MB) ocupen poco en el volumen y suban más rápido.
"""

import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

MAX_LADO = 1600
CALIDAD = 72


def comprimir_imagen(archivo, max_lado=MAX_LADO, calidad=CALIDAD, nombre=None):
    """Devuelve un ContentFile JPEG comprimido a partir de un archivo de imagen."""
    img = Image.open(archivo)
    # Corrige la orientación según los metadatos EXIF del celular.
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    # thumbnail solo reduce si la imagen es mayor; conserva la proporción.
    img.thumbnail((max_lado, max_lado))

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=calidad, optimize=True)
    buffer.seek(0)

    if nombre is None:
        base = getattr(archivo, "name", "foto")
        nombre = os.path.splitext(os.path.basename(base))[0] + ".jpg"
    return ContentFile(buffer.read(), name=nombre)
