from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("ingresar/", views.Ingresar.as_view(), name="login"),
    path("salir/", views.Salir.as_view(), name="logout"),
    path("perfil/", views.perfil, name="perfil"),
    path("privacidad/", views.privacidad, name="privacidad"),
]
