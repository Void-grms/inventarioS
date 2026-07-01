# Sistema de Verificación de Inventario Patrimonial — Diseño

**Fecha:** 2026-07-01
**Proyecto:** Verificación de inventario patrimonial del C.S.M.C. Renacer Otuzco
**Estado:** Diseño aprobado

## 1. Propósito

Aplicación web responsive (uso desde el celular, caminando por cada ambiente) para
**verificar físicamente los bienes patrimoniales** del Centro de Salud Mental Comunitario
Renacer Otuzco y **designar el responsable** de cada bien.

Hoy el inventario vive en un Excel (`Inventario C.S.M.C. Renacer Otuzco 2025.xlsx`) con
**385 bienes** repartidos en **20 servicios/ubicaciones**, y casi todos (381 de 385) están
a nombre de una sola persona. El objetivo real es recorrer los ambientes, confirmar la
existencia y estado de cada bien, y asignar el responsable correcto por servicio.

## 2. Alcance

**Incluye:**
- Login multi-usuario con trazabilidad de quién verificó.
- Navegación por servicio + búsqueda por código patrimonial o descripción.
- Ficha de bien con: asignar responsable, confirmar/actualizar estado y ubicación,
  marcar como faltante, tomar foto y agregar observación.
- Importación inicial desde el Excel existente.
- Reportes: por servicio, por responsable, tablero de avance, y exportación a Excel.
- Despliegue en Railway (PostgreSQL + volumen persistente para fotos).

**No incluye (YAGNI / futuro):**
- Etiquetas QR y escaneo con cámara (se puede añadir después).
- Modo offline / PWA sin internet (online-first en esta versión).
- App nativa de tienda (es web responsive).

## 3. Arquitectura

```
Celular (navegador) ──HTTPS──> Railway
                                 ├── App Django + gunicorn
                                 ├── PostgreSQL (datos)
                                 └── Volumen persistente /data (fotos)
```

- **Backend:** Django 5 + PostgreSQL. `gunicorn` como servidor de aplicación.
- **Estáticos:** `whitenoise` para servir CSS/JS sin infraestructura extra.
- **Frontend:** plantillas HTML de Django, mobile-first, con Bootstrap 5. JavaScript
  mínimo (buscador y captura de foto con la cámara del celular).
- **Online-first:** requiere conexión a internet en el centro.

## 4. Modelo de datos

### `Servicio`
Los 20 servicios/ubicaciones físicas (Terapia de Lenguaje, Auditorio, Farmacia, etc.).
- `nombre` (único)

### `Bien`
El bien patrimonial. Se carga desde el Excel y conserva todos los campos originales para
poder reexportar sin pérdida.
- `codigo_patrimonial` (único, indexado — clave de búsqueda)
- `descripcion`, `marca`, `modelo`, `nro_serie`, `color`, `medidas`, `caracteristicas`
- `servicio` (FK → `Servicio`)
- `estado` (choices: Bueno / Regular / Malo / Nuevo)
- `responsable` (texto libre, con autocompletado de nombres ya usados)
- `valor`, `fecha_alta` y demás campos del Excel (almacenados para reexportación fiel)
- **Campos de verificación:**
  - `estado_verificacion` (choices: Pendiente / Verificado / Faltante; default Pendiente)
  - `fecha_verificacion` (nullable)
  - `verificado_por` (FK → `Usuario`, nullable)

### `Foto`
Imágenes asociadas a un bien (puede haber varias).
- `bien` (FK → `Bien`)
- `imagen` (guardada en el volumen persistente; en la BD solo la ruta)
- `tomada_por` (FK → `Usuario`), `fecha`

### `RegistroVerificacion` (bitácora / auditoría)
Cada acción de campo, para trazabilidad.
- `bien` (FK), `verificador` (FK → `Usuario`), `fecha`
- `cambios` (qué se modificó: responsable / estado / ubicación / faltante)
- `observacion` (texto)

### `Usuario`
Sistema de auth de Django con dos roles:
- **Admin:** gestiona todo, importa el Excel, crea cuentas, ve reportes, panel `/admin`.
- **Verificador:** inicia sesión y registra verificaciones en campo.

## 5. Flujo de pantallas

1. **Login.**
2. **Inicio / Avance:** tarjetas por servicio con barra de progreso
   (ej. "Farmacia 8/15 verificados"). Búsqueda global arriba.
3. **Búsqueda:** por código patrimonial o parte de la descripción → resultados → ficha.
4. **Lista por servicio:** bienes del servicio con ícono de estado
   (⏳ pendiente / ✅ verificado / ❌ faltante).
5. **Ficha del bien:** muestra todos los datos y permite en una sola pantalla:
   - Asignar/cambiar **responsable** (autocompletado).
   - Confirmar/cambiar **estado** y **ubicación/servicio**.
   - **Marcar como faltante.**
   - **Tomar foto** (cámara del celular) + **observación**.
   - **Guardar verificación** → marca verificado, registra fecha + verificador, escribe
     en la bitácora.

## 6. Importación, reportes y exportación

- **Importar Excel:** management command que lee el `.xlsx`, crea servicios y bienes.
  Se corre una vez al inicio; idempotente para poder recargar.
- **Exportar a Excel:** inventario actualizado con el **mismo formato de columnas** del
  original + columnas nuevas (estado_verificacion, verificado_por, fecha_verificacion).
- **Reporte por servicio:** bienes agrupados por ambiente con su responsable
  (acta de entrega por servicio), imprimible/descargable.
- **Reporte por responsable:** bienes agrupados por persona (para firma de cargo).
- **Tablero de avance:** verificados / pendientes / faltantes, global y por servicio.

## 7. Almacenamiento de fotos

Volumen persistente de Railway montado en `/data`. En la BD se guarda solo la ruta.
Sobreviven a los redepliegues. Django sirve las imágenes protegidas (solo usuarios
autenticados).

## 8. Despliegue en Railway

- Repo con `requirements.txt`, comando de arranque (`gunicorn`) y variables de entorno:
  `DATABASE_URL`, `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `MEDIA_ROOT=/data`.
- PostgreSQL como servicio de Railway (provee `DATABASE_URL`).
- Volumen persistente montado en `/data` para las fotos.
- Al desplegar: correr migraciones, crear superusuario admin, y cargar el Excel inicial.
- HTTPS automático de Railway (requisito para que el celular permita usar la cámara).

## 9. Pruebas

- Modelos (`Bien`, `Servicio`, `Foto`, `RegistroVerificacion`).
- Importador de Excel: que los 385 bienes y 20 servicios carguen correctamente.
- Flujo de verificación: guardar cambios + creación de registro en bitácora.
- Reportes y exportación a Excel.
- Control de acceso: verificador vs. admin.
