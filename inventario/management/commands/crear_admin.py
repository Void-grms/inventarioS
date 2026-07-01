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
