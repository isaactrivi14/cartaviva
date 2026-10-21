from django.urls import path

from . import views

app_name = "inscripciones"

urlpatterns = [
    path("", views.mis_pases, name="mis_pases"),
    path("<int:pk>/", views.pase, name="pase"),
    path("<int:pk>/cancelar/", views.cancelar, name="cancelar"),
    path("inscribir/<int:evento_id>/", views.inscribir, name="inscribir"),
    path("escaner/<int:evento_id>/", views.escaner, name="escaner"),
    path("escaner/<int:evento_id>/validar/", views.validar, name="validar"),
]
