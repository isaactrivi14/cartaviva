from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cuenta/", include("usuarios.urls")),
    path("pases/", include("inscripciones.urls")),
    path("api/v1/", include("inscripciones.urls_api")),  # app móvil del escáner
    path("", include("eventos.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
