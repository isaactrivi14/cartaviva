import uuid

from django.conf import settings
from django.core import signing
from django.db import models

SALT_PASE = "cartaviva.pase.v1"


class Inscripcion(models.Model):
    evento = models.ForeignKey("eventos.Evento", on_delete=models.CASCADE, related_name="inscripciones")
    asistente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inscripciones")
    # Token aleatorio: no revela nada de la persona. Es lo único que va en el QR.
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    check_in_at = models.DateTimeField("hora de ingreso", null=True, blank=True)

    class Meta:
        verbose_name = "inscripción"
        verbose_name_plural = "inscripciones"
        constraints = [
            # Una persona no puede inscribirse dos veces al mismo evento (lo impone MySQL).
            models.UniqueConstraint(fields=["evento", "asistente"], name="inscripcion_unica_por_evento"),
        ]
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.asistente} → {self.evento}"

    @property
    def numero(self):
        return f"{self.pk:05d}"

    @property
    def codigo_qr(self):
        """
        Contenido del QR: el token FIRMADO con la SECRET_KEY del servidor.
        La firma impide que alguien invente un código válido. No va cifrado
        porque no hace falta: el token no contiene datos personales.
        """
        return signing.dumps(str(self.token), salt=SALT_PASE)

    @staticmethod
    def token_desde_codigo(codigo):
        """Devuelve el token si la firma es válida, o None si el código fue alterado."""
        try:
            return signing.loads(codigo, salt=SALT_PASE)
        except signing.BadSignature:
            return None
