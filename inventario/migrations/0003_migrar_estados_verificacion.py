from django.db import migrations


def a_nuevos_estados(apps, schema_editor):
    Bien = apps.get_model("inventario", "Bien")
    Bien.objects.filter(estado_verificacion="Verificado").update(
        estado_verificacion="CONFORME")
    Bien.objects.filter(estado_verificacion="Faltante").update(
        estado_verificacion="FALTANTE")


def a_estados_antiguos(apps, schema_editor):
    Bien = apps.get_model("inventario", "Bien")
    Bien.objects.filter(estado_verificacion="CONFORME").update(
        estado_verificacion="Verificado")
    Bien.objects.filter(estado_verificacion="FALTANTE").update(
        estado_verificacion="Faltante")
    # CAMBIADO y DAÑADO no existían antes; se dejan como Pendiente al revertir
    Bien.objects.filter(
        estado_verificacion__in=["CAMBIADO", "DAÑADO"]).update(
        estado_verificacion="Pendiente")


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0002_alter_bien_estado_verificacion"),
    ]

    operations = [
        migrations.RunPython(a_nuevos_estados, a_estados_antiguos),
    ]
