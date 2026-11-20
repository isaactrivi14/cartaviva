from django.urls import path

from . import api_movil

app_name = "api"

urlpatterns = [
    path("sesion", api_movil.sesion, name="sesion"),
    path("eventos", api_movil.eventos, name="eventos"),
    path("eventos/<int:evento_id>/validar", api_movil.validar, name="validar"),
]
