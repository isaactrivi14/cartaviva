"""
Muestra a qué base de datos está conectado Cartaviva y cuántos registros guarda.
Sirve para demostrar que los datos quedan en MySQL y no en el HTML.
Uso:  python manage.py estado_bd
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.utils import OperationalError

from eventos.models import Categoria, Evento
from inscripciones.models import Inscripcion
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Muestra el motor de base de datos, las migraciones pendientes y cuántos registros hay."

    def handle(self, *args, **opciones):
        bd = connection.settings_dict
        try:
            connection.ensure_connection()
        except OperationalError as error:
            raise CommandError(
                f"No se pudo conectar a «{bd['NAME']}» en {bd.get('HOST') or 'local'}. "
                f"Revisa que MySQL esté encendido y los datos DB_* del .env. Detalle: {error}"
            ) from error

        self.stdout.write(f"Motor:          {connection.display_name}")
        self.stdout.write(f"Base de datos:  {bd['NAME']}")
        if connection.vendor == "mysql":
            self.stdout.write(f"Servidor:       {bd['HOST']}:{bd['PORT']} (usuario {bd['USER']})")

        ejecutor = MigrationExecutor(connection)
        pendientes = ejecutor.migration_plan(ejecutor.loader.graph.leaf_nodes())
        if pendientes:
            self.stdout.write(self.style.WARNING(
                f"Migraciones:    faltan {len(pendientes)}. Corre: python manage.py migrate"
            ))
            return
        self.stdout.write("Migraciones:    al día")

        conteos = [
            ("Usuarios", Usuario.objects.count()),
            ("Categorías", Categoria.objects.count()),
            ("Eventos", Evento.objects.count()),
            ("Inscripciones", Inscripcion.objects.count()),
            ("Ingresos con QR", Inscripcion.objects.filter(check_in_at__isnull=False).count()),
        ]
        for nombre, total in conteos:
            self.stdout.write(f"  {nombre:<16}{total}")
        if connection.vendor != "mysql":
            self.stdout.write(self.style.WARNING("Ojo: estás en SQLite. Para la entrega pon DB_ENGINE=mysql en el .env"))
