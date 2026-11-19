from io import StringIO

import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_estado_bd_muestra_motor_y_cuenta_lo_guardado(hacer_evento):
    hacer_evento()
    salida = StringIO()
    call_command("estado_bd", stdout=salida)
    texto = salida.getvalue()
    assert "Migraciones:    al día" in texto
    assert "Eventos         1" in texto
    assert "Usuarios        1" in texto
