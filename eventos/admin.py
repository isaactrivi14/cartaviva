from django.contrib import admin

from .models import Categoria, Evento


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "color")


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "anfitrion", "fecha_inicio", "cupo_maximo", "es_relampago")
    list_filter = ("categoria", "es_relampago", "solo_mayores_18")
    search_fields = ("titulo", "barrio")
