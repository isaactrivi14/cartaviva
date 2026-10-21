from django.contrib import admin

from .models import Inscripcion


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ("evento", "asistente", "creado_en", "check_in_at")
    list_filter = ("evento",)
    readonly_fields = ("token",)
