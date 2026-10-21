from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("alias", "email", "rol", "is_active", "date_joined")
    list_filter = ("rol", "is_active")
    search_fields = ("alias", "email")
    fieldsets = UserAdmin.fieldsets + (
        ("Cartaviva", {"fields": ("rol", "alias", "foto", "fecha_nacimiento", "acepta_tratamiento_datos", "fecha_autorizacion")}),
    )
