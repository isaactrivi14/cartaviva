"""
Pruebas del CRUD de eventos (entidad central) y del flujo de sesión con sus mensajes.
"""
from datetime import timedelta

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from eventos.models import Evento
from inscripciones.models import Inscripcion

pytestmark = pytest.mark.django_db


def datos_evento(categoria, **cambios):
    inicio = timezone.localtime() + timedelta(days=2)
    datos = {
        "titulo": "Concierto en San Diego", "categoria": categoria.pk, "descripcion": "Música en vivo",
        "fecha_inicio": inicio.strftime("%Y-%m-%dT%H:%M"),
        "fecha_fin": (inicio + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M"),
        "direccion": "Plaza San Diego", "barrio": "San Diego",
        "latitud": "10.427800", "longitud": "-75.547600", "cupo_maximo": "50",
    }
    datos.update(cambios)
    return datos


def textos(respuesta):
    return [str(m) for m in get_messages(respuesta.wsgi_request)]


# --- CRUD de eventos -----------------------------------------------------------

def test_anfitrion_crea_evento_y_queda_guardado(client, anfitrion, categoria):
    client.force_login(anfitrion)
    respuesta = client.post(reverse("eventos:crear"), datos_evento(categoria))
    assert respuesta.status_code == 302
    evento = Evento.objects.get(titulo="Concierto en San Diego")
    assert evento.anfitrion == anfitrion
    assert "Publicaste «Concierto en San Diego». Ya aparece en el mapa." in textos(respuesta)


def test_anfitrion_edita_su_evento(client, anfitrion, categoria, hacer_evento):
    evento = hacer_evento()
    client.force_login(anfitrion)
    client.post(reverse("eventos:editar", args=[evento.pk]), datos_evento(categoria, titulo="Feria renovada", cupo_maximo="30"))
    evento.refresh_from_db()
    assert evento.titulo == "Feria renovada"
    assert evento.cupo_maximo == 30


def test_eliminar_evento_borra_tambien_sus_inscripciones(client, anfitrion, asistente, hacer_evento):
    evento = hacer_evento()
    Inscripcion.objects.create(evento=evento, asistente=asistente)
    client.force_login(anfitrion)
    client.post(reverse("eventos:eliminar", args=[evento.pk]))
    assert not Evento.objects.filter(pk=evento.pk).exists()
    assert Inscripcion.objects.count() == 0


def test_eliminar_no_acepta_get(client, anfitrion, hacer_evento):
    # Un enlace o una imagen no deben poder borrar un evento: solo POST con CSRF.
    evento = hacer_evento()
    client.force_login(anfitrion)
    respuesta = client.get(reverse("eventos:eliminar", args=[evento.pk]))
    assert respuesta.status_code == 405
    assert Evento.objects.filter(pk=evento.pk).exists()


def test_formulario_invalido_no_guarda_y_muestra_resumen_de_errores(client, anfitrion, categoria):
    client.force_login(anfitrion)
    respuesta = client.post(reverse("eventos:crear"), datos_evento(categoria, titulo="abc", cupo_maximo="0"))
    assert respuesta.status_code == 200
    html = respuesta.content.decode()
    assert 'id="resumen-errores"' in html
    assert "El título debe tener al menos 5 caracteres." in html
    assert Evento.objects.count() == 0


# --- Sesión --------------------------------------------------------------------

def test_login_y_logout_muestran_mensaje(client, asistente):
    respuesta = client.post(reverse("usuarios:login"), {"username": "ASISTENTE@test.co", "password": "ClaveSegura123!"})
    assert respuesta.status_code == 302
    assert "Hola de nuevo, asistente." in textos(respuesta)
    respuesta = client.post(reverse("usuarios:logout"))
    assert "Cerraste sesión." in textos(respuesta)
    assert "_auth_user_id" not in client.session
