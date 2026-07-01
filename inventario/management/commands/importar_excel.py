from django.core.management.base import BaseCommand

from inventario.importador import importar_inventario


class Command(BaseCommand):
    help = "Importa el inventario desde un archivo .xlsx"

    def add_arguments(self, parser):
        parser.add_argument("ruta", type=str)

    def handle(self, *args, **opts):
        creados, actualizados = importar_inventario(opts["ruta"])
        self.stdout.write(self.style.SUCCESS(
            f"Importados: {creados} nuevos, {actualizados} actualizados."))
