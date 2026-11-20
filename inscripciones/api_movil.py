"""
API para la app móvil del escáner (Cartaviva Escáner, hecha con Expo).

La app no usa la sesión ni las cookies del navegador: inicia sesión una vez y
recibe un token firmado que envía en cada petición (cabecera Authorization).
Solo pueden usarla los anfitriones y los administradores.

    POST /api/v1/sesion                    {usuario, clave} -> {token, alias, rol}
    GET  /api/v1/eventos                   eventos que el anfitrión puede escanear
    POST /api/v1/eventos/<id>/validar      {codigo, confirmar} -> misma respuesta que el escáner web
"""
import json
from datetime import timedelta
from functools import wraps

from django.contrib.auth import authenticate
from django.core import signing
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from eventos.models import Evento
from usuarios.models import Usuario

from .views import revisar_pase

SALT_TOKEN = "cartaviva.movil.v1"
DURACION_TOKEN = timedelta(hours=12)  # una jornada de evento; luego se vuelve a iniciar sesión


def crear_token(usuario):
    # La huella de la sesión cambia si cambia la contraseña: así un cambio de clave
    # invalida los tokens que ya se habían entregado.
    return signing.dumps({"u": usuario.pk, "h": usuario.get_session_auth_hash()}, salt=SALT_TOKEN, compress=True)


def usuario_desde_token(token):
    try:
        datos = signing.loads(token, salt=SALT_TOKEN, max_age=DURACION_TOKEN)
    except signing.BadSignature:  # incluye SignatureExpired
        return None
    usuario = Usuario.objects.filter(pk=datos.get("u"), is_active=True).first()
    if usuario is None or usuario.get_session_auth_hash() != datos.get("h"):
        return None
    return usuario


def _json(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


def token_requerido(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        cabecera = request.headers.get("Authorization", "")
        token = cabecera.removeprefix("Bearer ").strip() if cabecera.startswith("Bearer ") else ""
        usuario = usuario_desde_token(token) if token else None
        if usuario is None:
            return JsonResponse({"error": "Sesión vencida o inválida. Vuelve a iniciar sesión."}, status=401)
        if not (usuario.es_admin or usuario.es_anfitrion):
            return JsonResponse({"error": "Solo los anfitriones pueden usar el escáner."}, status=403)
        request.usuario_movil = usuario
        return vista(request, *args, **kwargs)
    return envoltura


@csrf_exempt  # sin cookies no hay riesgo de CSRF: la autenticación viaja en la cabecera
@require_POST
def sesion(request):
    datos = _json(request)
    usuario = authenticate(request, username=str(datos.get("usuario", "")).strip(), password=datos.get("clave", ""))
    if usuario is None:
        return JsonResponse({"error": "Usuario o contraseña incorrectos."}, status=400)
    if not (usuario.es_admin or usuario.es_anfitrion):
        return JsonResponse({"error": "Solo los anfitriones pueden usar el escáner."}, status=403)
    return JsonResponse({"token": crear_token(usuario), "alias": usuario.alias, "rol": usuario.rol,
                         "vence_en_horas": int(DURACION_TOKEN.total_seconds() // 3600)})


@require_GET
@token_requerido
def eventos(request):
    usuario = request.usuario_movil
    desde = timezone.now() - timedelta(days=1)
    consulta = Evento.objects.filter(fecha_fin__gte=desde)
    if not usuario.es_admin:
        consulta = consulta.filter(anfitrion=usuario)
    return JsonResponse({"eventos": [
        {"id": e.pk, "titulo": e.titulo, "barrio": e.barrio, "inicio": e.fecha_inicio.isoformat(),
         "fin": e.fecha_fin.isoformat(), "inscritos": e.inscritos, "ingresados": e.ingresados,
         "solo_mayores_18": e.solo_mayores_18}
        for e in consulta.order_by("fecha_inicio")[:50]
    ]})


@csrf_exempt
@require_POST
@token_requerido
def validar(request, evento_id):
    usuario = request.usuario_movil
    evento = get_object_or_404(Evento, pk=evento_id)
    if not (usuario.es_admin or evento.anfitrion_id == usuario.pk):
        return JsonResponse({"autorizado": False, "mensaje": "Este evento no es tuyo."}, status=403)
    datos = _json(request)
    return JsonResponse(revisar_pase(evento, datos.get("codigo", ""), bool(datos.get("confirmar")),
                                     construir_url=request.build_absolute_uri))
