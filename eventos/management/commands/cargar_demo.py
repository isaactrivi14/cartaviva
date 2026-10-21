"""
Carga datos de demostración en la base de datos (MySQL o SQLite):
categorías, usuarios de prueba de cada rol y eventos en barrios de Cartagena.

Uso:  python manage.py cargar_demo
      python manage.py cargar_demo --reiniciar   (borra los eventos y vuelve a crearlos)

Los datos quedan en la BD; ninguna pantalla tiene datos escritos a mano en el HTML.
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from eventos.models import Categoria, Evento
from inscripciones.models import Inscripcion
from usuarios.models import Usuario

CLAVE_DEMO = "Cartaviva2026!"

CATEGORIAS = [
    ("Cultura", "#0077B6"),
    ("Deporte", "#2A9D8F"),
    ("Música", "#D62839"),
    ("Gastronomía", "#F77F00"),
    ("Comunidad", "#6A4C93"),
]


class Command(BaseCommand):
    help = "Carga usuarios, categorías y eventos de demostración."

    def add_arguments(self, parser):
        parser.add_argument("--reiniciar", action="store_true", help="Borra los eventos existentes antes de cargar.")

    def usuario(self, email, alias, rol, años, **extra):
        nacimiento = date.today() - timedelta(days=365 * años + años // 4 + 30)
        u, creado = Usuario.objects.get_or_create(
            username=email,
            defaults={"email": email, "alias": alias, "rol": rol, "fecha_nacimiento": nacimiento,
                      "acepta_tratamiento_datos": True, "fecha_autorizacion": timezone.now(), **extra},
        )
        if creado:
            u.set_password(CLAVE_DEMO)
            u.save()
        return u

    def handle(self, *args, **opciones):
        if opciones["reiniciar"]:
            Evento.objects.all().delete()

        cats = {nombre: Categoria.objects.get_or_create(nombre=nombre, defaults={"color": color})[0] for nombre, color in CATEGORIAS}

        admin = self.usuario("admin@cartaviva.co", "Admin Cartaviva", Usuario.Rol.ADMIN, 30, is_staff=True, is_superuser=True)
        anfitrion = self.usuario("anfitrion@cartaviva.co", "ColectivoGetsemaní", Usuario.Rol.ANFITRION, 28)
        anfitrion2 = self.usuario("club@cartaviva.co", "ClubManga5", Usuario.Rol.ANFITRION, 35)
        asistente = self.usuario("asistente@cartaviva.co", "CaribeViajero", Usuario.Rol.ASISTENTE, 22)
        self.usuario("menor@cartaviva.co", "Juanes16", Usuario.Rol.ASISTENTE, 16)
        vecinos = [self.usuario(f"vecino{i}@cartaviva.co", f"Vecino{i}", Usuario.Rol.ASISTENTE, 20 + i) for i in range(1, 9)]

        if Evento.objects.exists():
            self.stdout.write(self.style.WARNING("Ya hay eventos. Usa --reiniciar para volver a crearlos."))
            self.resumen()
            return

        ahora = timezone.now().replace(second=0, microsecond=0)
        h = lambda horas: ahora + timedelta(hours=horas)

        def evento(anf, cat, titulo, barrio, direccion, lat, lng, inicio, horas, cupo, **extra):
            return Evento.objects.create(
                anfitrion=anf, categoria=cats[cat], titulo=titulo, barrio=barrio, direccion=direccion,
                latitud=lat, longitud=lng, fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=horas),
                cupo_maximo=cupo, descripcion=extra.pop("descripcion", "Evento comunitario abierto en Cartagena."), **extra,
            )

        feria = evento(anfitrion, "Gastronomía", "Feria de sabores en la Plaza de la Trinidad", "Getsemaní",
                       "Plaza de la Trinidad", 10.4206, -75.5458, h(48), 4, 80,
                       descripcion="Cocineras del barrio venden fritos, arepas de huevo y jugos naturales.\nTrae tu propio vaso.")
        futbol = evento(anfitrion2, "Deporte", "Fútbol 5 mixto en Manga", "Manga", "Cancha de la Calle Real de Manga",
                        10.4128, -75.5355, h(26), 2, 10, descripcion="Partido amistoso. Faltan jugadores para completar equipos.")
        champeta = evento(anfitrion, "Música", "Taller de champeta para principiantes", "Pie de la Popa",
                          "Casa de la cultura del barrio", 10.4178, -75.5300, h(-1), 3, 30,
                          descripcion="Clase abierta de baile con músicos en vivo.")
        evento(anfitrion, "Cultura", "Atardecer en el Baluarte de San Francisco Javier", "Centro Histórico",
               "Baluarte de San Francisco Javier", 10.4245, -75.5525, h(1), 3, 15, es_relampago=True,
               descripcion="Plan relámpago: nos vemos para ver el atardecer y tomar fotos en la muralla.")
        evento(anfitrion2, "Comunidad", "Limpieza de playa en La Boquilla", "La Boquilla", "Playa de La Boquilla, sector Los Morros",
               10.4740, -75.4925, h(72), 4, 40, descripcion="Jornada ambiental. Se entregan guantes y bolsas.")
        jazz = evento(anfitrion, "Música", "Noche de jazz en Bocagrande (+18)", "Bocagrande", "Terraza comunal, Carrera 2",
                      10.3990, -75.5560, h(96), 3, 5, solo_mayores_18=True, descripcion="Trío de jazz local. Evento para mayores de edad.")
        pasado = evento(anfitrion, "Deporte", "Ciclopaseo por la muralla", "Centro Histórico", "Torre del Reloj",
                        10.4227, -75.5495, h(-30), 2, 20, descripcion="Recorrido en bicicleta por el cordón amurallado.")

        # Inscripciones para que el mapa muestre estados distintos y haya métricas
        for v in vecinos[:8]:
            Inscripcion.objects.create(evento=futbol, asistente=v)          # 8/10 → últimos cupos
        for v in vecinos[:5]:
            Inscripcion.objects.create(evento=jazz, asistente=v)            # 5/5 → lleno
        for v in vecinos[:6]:
            Inscripcion.objects.create(evento=champeta, asistente=v)        # en vivo
        for v in vecinos[:4]:
            Inscripcion.objects.create(evento=feria, asistente=v)
        # Evento pasado: 6 inscritos, 4 entraron con QR → asistencia 67 %
        for i, v in enumerate(vecinos[:5] + [asistente]):
            Inscripcion.objects.create(evento=pasado, asistente=v, check_in_at=pasado.fecha_inicio + timedelta(minutes=10) if i < 3 or v == asistente else None)

        self.stdout.write(self.style.SUCCESS("Datos de demostración cargados."))
        self.resumen()

    def resumen(self):
        self.stdout.write(f"\nUsuarios de prueba (contraseña para todos: {CLAVE_DEMO})")
        self.stdout.write("  ADMIN      admin@cartaviva.co")
        self.stdout.write("  ANFITRIÓN  anfitrion@cartaviva.co")
        self.stdout.write("  ASISTENTE  asistente@cartaviva.co")
        self.stdout.write("  ASISTENTE  menor@cartaviva.co   (16 años, para probar eventos +18)")
