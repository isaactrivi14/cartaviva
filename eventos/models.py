from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

# Límites de Cartagena (aprox.) para validar que el evento quede en la ciudad.
LAT_MIN, LAT_MAX = 10.25, 10.55
LNG_MIN, LNG_MAX = -75.62, -75.38


class Categoria(models.Model):
    nombre = models.CharField(max_length=40, unique=True)
    color = models.CharField(max_length=7, default="#0077B6", help_text="Color hexadecimal, ej. #0077B6")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "categoría"

    def __str__(self):
        return self.nombre


class Evento(models.Model):
    """Entidad central del proyecto: sobre ella se hace el CRUD."""

    class Estado(models.TextChoices):
        ABIERTO = "ABIERTO", "Abierto"
        ULTIMOS = "ULTIMOS", "Últimos cupos"
        LLENO = "LLENO", "Lleno"
        EN_VIVO = "EN_VIVO", "En vivo"
        FINALIZADO = "FINALIZADO", "Finalizado"

    anfitrion = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eventos")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="eventos")
    titulo = models.CharField(max_length=80)
    descripcion = models.TextField(max_length=1500)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    direccion = models.CharField(max_length=120)
    barrio = models.CharField(max_length=60)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    cupo_maximo = models.PositiveIntegerField()
    solo_mayores_18 = models.BooleanField("Solo mayores de 18", default=False)
    es_relampago = models.BooleanField("Plan relámpago", default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha_inicio"]

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse("eventos:detalle", args=[self.pk])

    # --- Validaciones de negocio (se ejecutan en el servidor) -------------
    def clean(self):
        errores = {}
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_fin <= self.fecha_inicio:
                errores["fecha_fin"] = "La hora de fin debe ser posterior a la de inicio."
            duracion = self.fecha_fin - self.fecha_inicio
            if self.es_relampago and not (timedelta(hours=1) <= duracion <= timedelta(hours=6)):
                errores["fecha_fin"] = "Un plan relámpago debe durar entre 1 y 6 horas."
            if not self.pk and self.fecha_fin <= timezone.now():
                errores["fecha_fin"] = "No puedes publicar un evento que ya terminó."
        if self.cupo_maximo is not None and not (1 <= self.cupo_maximo <= 5000):
            errores["cupo_maximo"] = "El cupo debe estar entre 1 y 5000 personas."
        if self.latitud is not None and self.longitud is not None:
            if not (LAT_MIN <= float(self.latitud) <= LAT_MAX and LNG_MIN <= float(self.longitud) <= LNG_MAX):
                errores["latitud"] = "La ubicación debe estar dentro de Cartagena de Indias."
        if errores:
            raise ValidationError(errores)

    # --- Datos calculados -------------------------------------------------
    @property
    def inscritos(self):
        return self.inscripciones.count()

    @property
    def ingresados(self):
        return self.inscripciones.filter(check_in_at__isnull=False).count()

    @property
    def cupos_restantes(self):
        return max(self.cupo_maximo - self.inscritos, 0)

    @property
    def tasa_asistencia(self):
        """% de inscritos que realmente entraron con su QR."""
        inscritos = self.inscritos
        return round(self.ingresados * 100 / inscritos) if inscritos else 0

    @property
    def porcentaje_ocupacion(self):
        return round(self.inscritos * 100 / self.cupo_maximo) if self.cupo_maximo else 0

    @property
    def estado(self):
        """El estado se calcula, no se guarda: así nunca queda desactualizado."""
        ahora = timezone.now()
        if ahora > self.fecha_fin:
            return self.Estado.FINALIZADO
        if self.fecha_inicio <= ahora <= self.fecha_fin:
            return self.Estado.EN_VIVO
        restantes = self.cupos_restantes
        if restantes == 0:
            return self.Estado.LLENO
        if restantes <= max(1, self.cupo_maximo // 5):
            return self.Estado.ULTIMOS
        return self.Estado.ABIERTO

    @property
    def estado_label(self):
        return self.Estado(self.estado).label

    @property
    def acepta_inscripciones(self):
        return self.estado in (self.Estado.ABIERTO, self.Estado.ULTIMOS, self.Estado.EN_VIVO) and self.cupos_restantes > 0

    @property
    def horas_para_vencer(self):
        segundos = (self.fecha_fin - timezone.now()).total_seconds()
        return max(round(segundos / 3600, 1), 0)
