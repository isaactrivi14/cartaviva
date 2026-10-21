from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import LoginForm, RegistroForm


def registro(request):
    if request.user.is_authenticated:
        return redirect("eventos:explorar")
    if request.method == "POST":
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f"¡Bienvenido a Cartaviva, {usuario.alias}!")
            return redirect("eventos:explorar")
        messages.error(request, "Revisa los campos marcados.")
    else:
        form = RegistroForm()
    return render(request, "usuarios/registro.html", {"form": form})


class Ingresar(LoginView):
    template_name = "usuarios/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Hola de nuevo, {form.get_user().alias}.")
        return super().form_valid(form)


class Salir(LogoutView):
    def post(self, request, *args, **kwargs):
        messages.info(request, "Cerraste sesión.")
        return super().post(request, *args, **kwargs)


@login_required
def perfil(request):
    return render(request, "usuarios/perfil.html", {"pasaporte": request.user.pasaporte()})


def privacidad(request):
    return render(request, "usuarios/privacidad.html")
