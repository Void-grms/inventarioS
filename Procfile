web: gunicorn config.wsgi --bind 0.0.0.0:$PORT
release: python manage.py migrate --noinput && python manage.py crear_admin && python manage.py collectstatic --noinput
