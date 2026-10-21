from django.urls import path

from . import views

app_name = "eventos"

urlpatterns = [
    path("", views.explorar, name="explorar"),
    path("api/eventos/", views.api_eventos, name="api"),
    path("eventos/<int:pk>/", views.detalle, name="detalle"),
    path("anfitrion/", views.panel, name="panel"),
    path("anfitrion/eventos/nuevo/", views.crear, name="crear"),
    path("anfitrion/eventos/<int:pk>/editar/", views.editar, name="editar"),
    path("anfitrion/eventos/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
