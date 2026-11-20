"""Pruebas de la API de la app móvil del escáner (token firmado, sin cookies ni CSRF)."""
import json
from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from inscripciones.api_movil import crear_token
from inscripciones.models import Inscripcion
from usuarios.models import Usuario

from .conftest import crear_usuario

pytestmark = pytest.mark.django_db

CLAVE = "ClaveSegura123!"


@pytest.fixture
def api():
    # enforce_csrf_checks: la app móvil no tiene cookie CSRF, así que la API debe funcionar sin ella
    return Client(enforce_csrf_checks=True)


def post(api, nombre, datos, token=None, args=None):
    extra = {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}
    return api.post(reverse(f"api:{nombre}", args=args), data=json.dumps(datos), content_type="application/json", **extra)


def test_inicio_de_sesion_entrega_token_solo_a_anfitriones(api, anfitrion, asistente):
    r = post(api, "sesion", {"usuario": anfitrion.username, "clave": CLAVE})
    assert r.status_code == 200
    assert r.json()["token"] and r.json()["alias"] == anfitrion.alias

    assert post(api, "sesion", {"usuario": anfitrion.username, "clave": "mala"}).status_code == 400
    assert post(api, "sesion", {"usuario": asistente.username, "clave": CLAVE}).status_code == 403


def test_sin_token_o_con_token_alterado_responde_401(api, anfitrion):
    assert api.get(reverse("api:eventos")).status_code == 401
    token = crear_token(anfitrion)
    r = api.get(reverse("api:eventos"), HTTP_AUTHORIZATION=f"Bearer {token[:-3]}abc")
    assert r.status_code == 401


def test_cambiar_la_contrasena_invalida_el_token(api, anfitrion):
    token = crear_token(anfitrion)
    anfitrion.set_password("OtraClaveSegura456!")
    anfitrion.save()
    assert api.get(reverse("api:eventos"), HTTP_AUTHORIZATION=f"Bearer {token}").status_code == 401


def test_lista_solo_los_eventos_propios_y_vigentes(api, anfitrion, hacer_evento):
    hacer_evento(titulo="Mi evento")
    hacer_evento(titulo="Evento terminado", inicio=timezone.now() - timedelta(days=3))
    otro = crear_usuario("otro@test.co", Usuario.Rol.ANFITRION)
    hacer_evento(titulo="Evento ajeno", anfitrion=otro)

    r = api.get(reverse("api:eventos"), HTTP_AUTHORIZATION=f"Bearer {crear_token(anfitrion)}")
    titulos = [e["titulo"] for e in r.json()["eventos"]]
    assert titulos == ["Mi evento"]


def test_validar_y_registrar_ingreso_desde_la_app(api, anfitrion, asistente, hacer_evento):
    evento = hacer_evento()
    inscripcion = Inscripcion.objects.create(evento=evento, asistente=asistente)
    token = crear_token(anfitrion)

    revisado = post(api, "validar", {"codigo": inscripcion.codigo_qr}, token, [evento.pk]).json()
    assert revisado["autorizado"] and not revisado["registrado"]

    datos = post(api, "validar", {"codigo": inscripcion.codigo_qr, "confirmar": True}, token, [evento.pk]).json()
    assert datos["registrado"] and datos["ingresados"] == 1
    assert asistente.email not in json.dumps(datos)  # validación ciega: nada de datos personales

    otra_vez = post(api, "validar", {"codigo": inscripcion.codigo_qr, "confirmar": True}, token, [evento.pk]).json()
    assert otra_vez["autorizado"] is False


def test_no_se_pueden_escanear_eventos_ajenos(api, asistente, hacer_evento):
    evento = hacer_evento()
    inscripcion = Inscripcion.objects.create(evento=evento, asistente=asistente)
    otro = crear_usuario("otro@test.co", Usuario.Rol.ANFITRION)
    r = post(api, "validar", {"codigo": inscripcion.codigo_qr, "confirmar": True}, crear_token(otro), [evento.pk])
    assert r.status_code == 403
    inscripcion.refresh_from_db()
    assert inscripcion.check_in_at is None
