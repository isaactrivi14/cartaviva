from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from eventos.models import Categoria, Evento
from usuarios.models import Usuario


def crear_usuario(email, rol=Usuario.Rol.ASISTENTE, años=25):
    return Usuario.objects.create_user(
        username=email, email=email, password="ClaveSegura123!", alias=email.split("@")[0], rol=rol,
        fecha_nacimiento=date.today() - timedelta(days=365 * años + años // 4 + 10),
        acepta_tratamiento_datos=True,
    )


@pytest.fixture(autouse=True)
def sin_redireccion_https(settings):
    # Si el .env tiene DEBUG=False, el cliente de pruebas recibiría 301 hacia HTTPS.
    settings.SECURE_SSL_REDIRECT = False


@pytest.fixture
def anfitrion(db):
    return crear_usuario("anfitrion@test.co", Usuario.Rol.ANFITRION)


@pytest.fixture
def asistente(db):
    return crear_usuario("asistente@test.co")


@pytest.fixture
def menor(db):
    return crear_usuario("menor@test.co", años=16)


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre="Cultura")


@pytest.fixture
def hacer_evento(anfitrion, categoria):
    def _hacer(**datos):
        inicio = datos.pop("inicio", timezone.now() + timedelta(days=1))
        valores = {
            "anfitrion": anfitrion, "categoria": categoria, "titulo": "Feria en Getsemaní", "descripcion": "Prueba",
            "fecha_inicio": inicio, "fecha_fin": inicio + timedelta(hours=datos.pop("horas", 3)),
            "direccion": "Plaza de la Trinidad", "barrio": "Getsemaní",
            "latitud": Decimal("10.420600"), "longitud": Decimal("-75.545800"), "cupo_maximo": 10,
        }
        valores.update(datos)
        return Evento.objects.create(**valores)
    return _hacer
