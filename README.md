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

## Uso

- **Verificadores:** se crean desde el panel `/admin` (usuarios sin `is_staff`, o con
  `is_staff` para acceder al admin). Inician sesión y registran verificaciones en campo.
- **Flujo en campo:** login → avance por servicio → abrir servicio o buscar por
  código/descripción → ficha del bien → asignar responsable, confirmar estado/ubicación,
  marcar faltante, tomar foto y observación → guardar.
- **Reportes:** por servicio, por responsable, y exportación a Excel.
