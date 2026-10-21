from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario personalizado. Se define ANTES de la primera migración porque Django
    no permite cambiar el modelo de usuario después sin rehacer la base de datos.

    Minimización de datos (Ley 1581 de 2012): no guardamos cédula ni teléfono.
    Solo lo necesario: alias y foto (lo que ve el anfitrión), correo (para entrar)
    y fecha de nacimiento (para saber si es mayor de 18).
    """

    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        ANFITRION = "ANFITRION", "Anfitrión"
        ASISTENTE = "ASISTENTE", "Asistente"

    rol = models.CharField(max_length=10, choices=Rol.choices, default=Rol.ASISTENTE)
    alias = models.CharField(max_length=40, unique=True)
    foto = models.ImageField(upload_to="fotos/", blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    acepta_tratamiento_datos = models.BooleanField(default=False)
    fecha_autorizacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.alias or self.username

    # --- Roles -----------------------------------------------------------
    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN or self.is_superuser

    @property
    def es_anfitrion(self):
        return self.rol == self.Rol.ANFITRION

    @property
    def es_asistente(self):
        return self.rol == self.Rol.ASISTENTE

    # --- Edad ------------------------------------------------------------
    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        hoy = date.today()
        cumplio = (hoy.month, hoy.day) >= (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        return hoy.year - self.fecha_nacimiento.year - (0 if cumplio else 1)

    @property
    def es_mayor_de_edad(self):
        return self.edad is not None and self.edad >= 18

    # --- Pasaporte Cartagenero (reputación) -------------------------------
    def pasaporte(self):
        """
        Mide la confiabilidad real del usuario: de los eventos que ya terminaron
        y a los que se inscribió, ¿a cuántos entró con su QR?
        """
        from django.utils import timezone

        terminadas = self.inscripciones.filter(evento__fecha_fin__lt=timezone.now())
        total = terminadas.count()
        asistio = terminadas.filter(check_in_at__isnull=False).count()
        tasa = round(asistio * 100 / total) if total else None

        if total < 3:
            nivel = "Nuevo"
        elif tasa >= 90 and total >= 10:
            nivel = "Embajador"
        elif tasa >= 70:
            nivel = "Confiable"
        else:
            nivel = "En construcción"
        return {"eventos": total, "asistencias": asistio, "tasa": tasa, "nivel": nivel}
