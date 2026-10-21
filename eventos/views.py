from datetime import timedelta
from math import asin, cos, radians, sin, sqrt

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from usuarios.models import Usuario
from usuarios.permisos import rol_requerido

from .forms import EventoForm
from .models import Categoria, Evento


def distancia_km(lat1, lng1, lat2, lng2):
    """Fórmula de Haversine: distancia en km entre dos puntos del planeta."""
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2
    return 6371 * 2 * asin(sqrt(a))


def eventos_filtrados(params):
    """Aplica los filtros de fecha, categoría y distancia. Lo usan el mapa y la API."""
    ahora = timezone.now()
    eventos = Evento.objects.filter(fecha_fin__gte=ahora).select_related("categoria", "anfitrion")

    categoria = params.get("categoria")
    if categoria and categoria.isdigit():
        eventos = eventos.filter(categoria_id=int(categoria))

    fecha = params.get("fecha", "todas")
    if fecha == "hoy":
        fin_del_dia = timezone.localtime(ahora).replace(hour=23, minute=59, second=59)
        eventos = eventos.filter(fecha_inicio__lte=fin_del_dia)
    elif fecha == "semana":
        eventos = eventos.filter(fecha_inicio__lte=ahora + timedelta(days=7))

    if params.get("relampago") == "1":
        eventos = eventos.filter(es_relampago=True)

    resultado = list(eventos)
    try:
        lat, lng, km = float(params["lat"]), float(params["lng"]), float(params.get("km", 5))
    except (KeyError, ValueError):
        return resultado, None
    for e in resultado:
        e.distancia = distancia_km(lat, lng, float(e.latitud), float(e.longitud))
    resultado = sorted([e for e in resultado if e.distancia <= km], key=lambda e: e.distancia)
    return resultado, (lat, lng)


def explorar(request):
    eventos, _ = eventos_filtrados(request.GET)
    return render(request, "eventos/explorar.html", {
        "eventos": eventos,
        "categorias": Categoria.objects.all(),
        "filtros": request.GET,
        "centro": {"lat": settings.CARTAGENA_LAT, "lng": settings.CARTAGENA_LNG},
    })


def api_eventos(request):
    """Endpoint JSON que consume el mapa (los datos salen de la BD, no del HTML)."""
    eventos, _ = eventos_filtrados(request.GET)
    datos = [{
        "id": e.pk,
        "titulo": e.titulo,
        "categoria": e.categoria.nombre,
        "color": e.categoria.color,
        "lat": float(e.latitud),
        "lng": float(e.longitud),
        "estado": e.estado,
        "estado_label": e.estado_label,
        "relampago": e.es_relampago,
        "inicio": timezone.localtime(e.fecha_inicio).strftime("%d/%m %I:%M %p"),
        "barrio": e.barrio,
        "cupos_restantes": e.cupos_restantes,
        "distancia": round(e.distancia, 1) if hasattr(e, "distancia") else None,
        "url": e.get_absolute_url(),
    } for e in eventos]
    return JsonResponse({"eventos": datos})


def detalle(request, pk):
    evento = get_object_or_404(Evento.objects.select_related("categoria", "anfitrion"), pk=pk)
    inscripcion = None
    if request.user.is_authenticated:
        inscripcion = evento.inscripciones.filter(asistente=request.user).first()
    return render(request, "eventos/detalle.html", {
        "evento": evento,
        "inscripcion": inscripcion,
        "pasaporte_anfitrion": evento.anfitrion.pasaporte(),
    })


# --- CRUD del anfitrión ----------------------------------------------------

def _evento_propio(request, pk):
    """El anfitrión solo puede tocar SUS eventos; el admin puede tocar todos."""
    evento = get_object_or_404(Evento, pk=pk)
    if not (request.user.es_admin or evento.anfitrion_id == request.user.pk):
        return None
    return evento


@rol_requerido(Usuario.Rol.ANFITRION)
def panel(request):
    eventos = Evento.objects.select_related("categoria")
    if not request.user.es_admin:
        eventos = eventos.filter(anfitrion=request.user)
    eventos = list(eventos.order_by("-fecha_inicio"))
    total_inscritos = sum(e.inscritos for e in eventos)
    total_ingresados = sum(e.ingresados for e in eventos)
    return render(request, "eventos/panel.html", {
        "eventos": eventos,
        "total_inscritos": total_inscritos,
        "total_ingresados": total_ingresados,
        "tasa_global": round(total_ingresados * 100 / total_inscritos) if total_inscritos else 0,
    })


@rol_requerido(Usuario.Rol.ANFITRION)
def crear(request):
    form = EventoForm(request.POST or None)
    if request.method == "POST":
        form.instance.anfitrion = request.user
        if form.is_valid():
            evento = form.save()
            messages.success(request, f"Publicaste «{evento.titulo}». Ya aparece en el mapa.")
            return redirect("eventos:panel")
        messages.error(request, "No se pudo guardar. Revisa los campos marcados.")
    return render(request, "eventos/formulario.html", {"form": form, "modo": "crear", "centro": _centro()})


@rol_requerido(Usuario.Rol.ANFITRION)
def editar(request, pk):
    evento = _evento_propio(request, pk)
    if evento is None:
        messages.error(request, "Solo puedes editar tus propios eventos.")
        return redirect("eventos:panel")
    form = EventoForm(request.POST or None, instance=evento)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Cambios guardados.")
            return redirect("eventos:panel")
        messages.error(request, "No se pudo guardar. Revisa los campos marcados.")
    return render(request, "eventos/formulario.html", {"form": form, "modo": "editar", "evento": evento, "centro": _centro()})


@rol_requerido(Usuario.Rol.ANFITRION)
@require_POST
def eliminar(request, pk):
    evento = _evento_propio(request, pk)
    if evento is None:
        messages.error(request, "Solo puedes eliminar tus propios eventos.")
        return redirect("eventos:panel")
    titulo = evento.titulo
    evento.delete()
    messages.success(request, f"Eliminaste «{titulo}».")
    return redirect("eventos:panel")


def _centro():
    return {"lat": settings.CARTAGENA_LAT, "lng": settings.CARTAGENA_LNG}
