from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def rol_requerido(*roles):
    """
    Decorador para vistas: exige iniciar sesión y tener uno de los roles dados.
    El ADMIN siempre pasa. Si no tiene permiso, se muestra un mensaje y se
    redirige al inicio (en lugar de un error en blanco).
    """

    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(request, *args, **kwargs):
            usuario = request.user
            if usuario.es_admin or usuario.rol in roles:
                return vista(request, *args, **kwargs)
            messages.error(request, "No tienes permiso para entrar a esa página con tu rol actual.")
            return redirect("eventos:explorar")

        return envoltura

    return decorador
