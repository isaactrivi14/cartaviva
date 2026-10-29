"""
Pruebas automatizadas de Cartaviva (pytest + pytest-django).
Cubren modelos, validaciones, formularios, permisos por rol y la validación ciega del QR.
Ejecutar:  pytest -v
"""
import json
import os
import secrets
import subprocess
import sys
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from eventos.models import Evento
from inscripciones.models import Inscripcion
from usuarios.forms import RegistroForm

from .conftest import crear_usuario

pytestmark = pytest.mark.django_db


# --- Modelos -----------------------------------------------------------------

def test_estado_del_evento_se_calcula_por_cupos_y_fechas(hacer_evento):
    evento = hacer_evento(cupo_maximo=5)
    assert evento.estado == Evento.Estado.ABIERTO

    for i in range(4):
        Inscripcion.objects.create(evento=evento, asistente=crear_usuario(f"v{i}@test.co"))
    assert evento.estado == Evento.Estado.ULTIMOS

    Inscripcion.objects.create(evento=evento, asistente=crear_usuario("v9@test.co"))
    assert evento.estado == Evento.Estado.LLENO

    en_vivo = hacer_evento(inicio=timezone.now() - timedelta(minutes=30))
    assert en_vivo.estado == Evento.Estado.EN_VIVO


def test_tasa_de_asistencia_efectiva(hacer_evento):
    evento = hacer_evento()
    for i in range(4):
        Inscripcion.objects.create(evento=evento, asistente=crear_usuario(f"a{i}@test.co"),
                                   check_in_at=timezone.now() if i == 0 else None)
    assert evento.inscritos == 4
    assert evento.ingresados == 1
    assert evento.tasa_asistencia == 25


# --- Validaciones del servidor -------------------------------------------------

def test_plan_relampago_debe_durar_entre_1_y_6_horas(hacer_evento):
    evento = hacer_evento(es_relampago=True, horas=8)
    with pytest.raises(ValidationError) as error:
        evento.full_clean()
    assert "fecha_fin" in error.value.message_dict

    evento.fecha_fin = evento.fecha_inicio + timedelta(hours=2)
    evento.full_clean()  # 2 horas sí es válido


def test_evento_debe_estar_dentro_de_cartagena(hacer_evento):
    evento = hacer_evento(latitud=Decimal("4.711000"), longitud=Decimal("-74.072100"))  # Bogotá
    with pytest.raises(ValidationError) as error:
        evento.full_clean()
    assert "latitud" in error.value.message_dict


# --- Formularios ----------------------------------------------------------------

def test_registro_exige_autorizacion_de_datos(db):
    datos = {
        "alias": "Nuevo", "email": "nuevo@test.co", "fecha_nacimiento": "2000-01-15", "rol": "ASISTENTE",
        "password1": "ClaveSegura123!", "password2": "ClaveSegura123!",
    }
    form = RegistroForm(data=datos)
    assert not form.is_valid()
    assert "acepta_tratamiento_datos" in form.errors

    form = RegistroForm(data={**datos, "acepta_tratamiento_datos": "on"})
    assert form.is_valid(), form.errors
    usuario = form.save()
    assert usuario.acepta_tratamiento_datos and usuario.fecha_autorizacion is not None


# --- Reglas de negocio de la inscripción ------------------------------------

def test_menor_de_edad_no_puede_inscribirse_a_evento_18(client, menor, hacer_evento):
    evento = hacer_evento(solo_mayores_18=True)
    client.force_login(menor)
    client.post(reverse("inscripciones:inscribir", args=[evento.pk]))
    assert not Inscripcion.objects.filter(evento=evento, asistente=menor).exists()


def test_no_se_puede_inscribir_dos_veces_ni_con_evento_lleno(client, asistente, hacer_evento):
    evento = hacer_evento(cupo_maximo=1)
    client.force_login(asistente)
    client.post(reverse("inscripciones:inscribir", args=[evento.pk]))
    client.post(reverse("inscripciones:inscribir", args=[evento.pk]))
    assert evento.inscripciones.count() == 1

    otro = crear_usuario("otro@test.co")
    client.force_login(otro)
    client.post(reverse("inscripciones:inscribir", args=[evento.pk]))
    assert evento.inscripciones.count() == 1  # ya no había cupo


# --- Permisos por rol -----------------------------------------------------------

def test_asistente_no_puede_crear_eventos(client, asistente, categoria):
    client.force_login(asistente)
    respuesta = client.post(reverse("eventos:crear"), {"titulo": "Evento pirata"})
    assert respuesta.status_code == 302
    assert not Evento.objects.filter(titulo="Evento pirata").exists()


def test_anfitrion_no_puede_editar_ni_eliminar_evento_ajeno(client, hacer_evento):
    evento = hacer_evento()
    intruso = crear_usuario("intruso@test.co", rol="ANFITRION")
    client.force_login(intruso)
    client.post(reverse("eventos:eliminar", args=[evento.pk]))
    assert Evento.objects.filter(pk=evento.pk).exists()


# --- Check-in QR con validación ciega ------------------------------------------

def test_validacion_ciega_no_expone_datos_y_el_pase_no_se_reutiliza(client, anfitrion, asistente, hacer_evento):
    evento = hacer_evento()
    inscripcion = Inscripcion.objects.create(evento=evento, asistente=asistente)
    url = reverse("inscripciones:validar", args=[evento.pk])
    client.force_login(anfitrion)

    def validar(codigo, confirmar=False):
        r = client.post(url, data=json.dumps({"codigo": codigo, "confirmar": confirmar}), content_type="application/json")
        return r.json()

    datos = validar(inscripcion.codigo_qr, confirmar=True)
    assert datos["autorizado"] and datos["registrado"]
    assert datos["alias"] == asistente.alias
    # Solo foto, alias, +18 y estado del pase: nada de correo ni fecha de nacimiento
    assert set(datos) <= {"alias", "foto", "mayor_18", "ya_ingreso", "autorizado", "registrado", "mensaje", "ingresados", "inscritos"}
    assert asistente.email not in json.dumps(datos)

    # El mismo QR no sirve dos veces
    assert validar(inscripcion.codigo_qr)["autorizado"] is False

    # Un código alterado se rechaza por la firma
    assert validar(inscripcion.codigo_qr[:-2] + "xx")["autorizado"] is False


def test_api_del_mapa_devuelve_eventos_de_la_bd_sin_los_finalizados(client, hacer_evento):
    hacer_evento(titulo="Evento vigente")
    hacer_evento(titulo="Evento viejo", inicio=timezone.now() - timedelta(days=2))
    datos = client.get(reverse("eventos:api")).json()
    titulos = [e["titulo"] for e in datos["eventos"]]
    assert "Evento vigente" in titulos
    assert "Evento viejo" not in titulos


def test_configuracion_de_produccion_pasa_check_deploy():
    # Arranca Django como en el servidor (DEBUG=False) y exige cero advertencias de seguridad.
    entorno = {**os.environ, "DEBUG": "False", "SECRET_KEY": secrets.token_urlsafe(50), "DB_ENGINE": "sqlite"}
    resultado = subprocess.run(
        [sys.executable, "manage.py", "check", "--deploy", "--fail-level", "WARNING"],
        cwd=Path(__file__).resolve().parent.parent, env=entorno, capture_output=True, text=True,
    )
    assert resultado.returncode == 0, resultado.stderr + resultado.stdout
