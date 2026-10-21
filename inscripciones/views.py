import json

import qrcode
import qrcode.image.svg
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from eventos.models import Evento
from usuarios.models import Usuario
from usuarios.permisos import rol_requerido

from .models import Inscripcion


def validar_inscripcion(usuario, evento):
    """Reglas de negocio para inscribirse. Devuelve un mensaje de error o None."""
    if not usuario.es_asistente:
        return "Solo las cuentas de Asistente pueden inscribirse a eventos."
    if evento.anfitrion_id == usuario.pk:
        return "No puedes inscribirte a tu propio evento."
    if not evento.acepta_inscripciones:
        return f"Este evento ya no recibe inscripciones ({evento.estado_label.lower()})."
    if evento.solo_mayores_18 and not usuario.es_mayor_de_edad:
        return "Este evento es solo para mayores de 18 años."
    if evento.inscripciones.filter(asistente=usuario).exists():
        return "Ya estás inscrito a este evento."
    return None


@rol_requerido(Usuario.Rol.ASISTENTE)
@require_POST
def inscribir(request, evento_id):
    with transaction.atomic():
        # select_for_update bloquea la fila del evento para que dos personas no
        # tomen el último cupo al mismo tiempo.
        evento = get_object_or_404(Evento.objects.select_for_update(), pk=evento_id)
        error = validar_inscripcion(request.user, evento)
        if error:
            messages.error(request, error)
            return redirect(evento)
        try:
            inscripcion = Inscripcion.objects.create(evento=evento, asistente=request.user)
        except IntegrityError:
            messages.error(request, "Ya estás inscrito a este evento.")
            return redirect(evento)
    messages.success(request, "¡Listo! Este es tu pase. Muéstralo en la entrada.")
    return redirect("inscripciones:pase", pk=inscripcion.pk)


@login_required
@require_POST
def cancelar(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk, asistente=request.user)
    if inscripcion.check_in_at:
        messages.error(request, "No puedes cancelar un pase que ya se usó.")
    else:
        evento = inscripcion.evento
        inscripcion.delete()
        messages.info(request, f"Cancelaste tu inscripción a «{evento.titulo}». El cupo quedó libre.")
    return redirect("inscripciones:mis_pases")


@login_required
def mis_pases(request):
    inscripciones = request.user.inscripciones.select_related("evento", "evento__categoria")
    return render(request, "inscripciones/mis_pases.html", {"inscripciones": inscripciones})


@login_required
def pase(request, pk):
    inscripcion = get_object_or_404(Inscripcion.objects.select_related("evento"), pk=pk, asistente=request.user)
    imagen = qrcode.make(inscripcion.codigo_qr, image_factory=qrcode.image.svg.SvgPathImage, box_size=12, border=2)
    return render(request, "inscripciones/pase.html", {
        "inscripcion": inscripcion,
        "qr_svg": imagen.to_string(encoding="unicode"),
    })


# --- Escáner del anfitrión -------------------------------------------------

@rol_requerido(Usuario.Rol.ANFITRION)
def escaner(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    if not (request.user.es_admin or evento.anfitrion_id == request.user.pk):
        messages.error(request, "Solo puedes escanear pases de tus propios eventos.")
        return redirect("eventos:panel")
    return render(request, "inscripciones/escaner.html", {"evento": evento})


@rol_requerido(Usuario.Rol.ANFITRION)
@require_POST
def validar(request, evento_id):
    """
    VALIDACIÓN CIEGA. Recibe el código leído por la cámara y responde SOLO:
    foto, alias, si el pase está autorizado y si es mayor de 18.
    Nunca devuelve correo, fecha de nacimiento ni ningún otro dato personal.
    Si confirmar=true, además registra la hora de ingreso (check-in).
    """
    evento = get_object_or_404(Evento, pk=evento_id)
    if not (request.user.es_admin or evento.anfitrion_id == request.user.pk):
        return JsonResponse({"autorizado": False, "mensaje": "Este evento no es tuyo."}, status=403)

    try:
        datos = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        datos = {}
    codigo = str(datos.get("codigo", "")).strip()
    confirmar = bool(datos.get("confirmar"))

    token = Inscripcion.token_desde_codigo(codigo)
    if token is None:
        return JsonResponse({"autorizado": False, "mensaje": "Código inválido o alterado."})

    inscripcion = Inscripcion.objects.select_related("asistente").filter(token=token).first()
    if inscripcion is None or inscripcion.evento_id != evento.pk:
        return JsonResponse({"autorizado": False, "mensaje": "Este pase no es de este evento."})

    asistente = inscripcion.asistente
    respuesta = {
        "alias": asistente.alias,
        "foto": asistente.foto.url if asistente.foto else None,
        "mayor_18": asistente.es_mayor_de_edad,
        "ya_ingreso": inscripcion.check_in_at is not None,
    }

    if inscripcion.check_in_at:
        hora = timezone.localtime(inscripcion.check_in_at).strftime("%I:%M %p")
        return JsonResponse({**respuesta, "autorizado": False, "mensaje": f"Este pase ya se usó a las {hora}."})
    if evento.solo_mayores_18 and not asistente.es_mayor_de_edad:
        return JsonResponse({**respuesta, "autorizado": False, "mensaje": "Evento solo para mayores de 18."})

    if confirmar:
        inscripcion.check_in_at = timezone.now()
        inscripcion.save(update_fields=["check_in_at"])
        return JsonResponse({**respuesta, "autorizado": True, "registrado": True,
                             "mensaje": "Ingreso registrado.", "ingresados": evento.ingresados, "inscritos": evento.inscritos})

    return JsonResponse({**respuesta, "autorizado": True, "registrado": False, "mensaje": "Pase autorizado."})
