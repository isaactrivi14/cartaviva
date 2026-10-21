from datetime import date

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone

from .models import Usuario


class RegistroForm(UserCreationForm):
    """Registro con validaciones del lado del servidor (no confiamos solo en JS)."""

    ROLES_PERMITIDOS = [
        (Usuario.Rol.ASISTENTE, "Asistente: quiero ir a eventos"),
        (Usuario.Rol.ANFITRION, "Anfitrión: quiero publicar eventos"),
    ]

    rol = forms.ChoiceField(choices=ROLES_PERMITIDOS, widget=forms.RadioSelect, initial=Usuario.Rol.ASISTENTE)
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Fecha de nacimiento")
    acepta_tratamiento_datos = forms.BooleanField(
        required=True,
        label="Autorizo el tratamiento de mis datos personales según la Ley 1581 de 2012 y la política de privacidad.",
        error_messages={"required": "Debes autorizar el tratamiento de datos para crear la cuenta."},
    )

    class Meta:
        model = Usuario
        fields = ["alias", "email", "foto", "fecha_nacimiento", "rol"]
        labels = {"alias": "Alias", "email": "Correo", "foto": "Foto de perfil"}
        help_texts = {"alias": "Así te verá el anfitrión en la puerta. No uses tu nombre completo si no quieres."}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not email:
            raise forms.ValidationError("El correo es obligatorio.")
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data["fecha_nacimiento"]
        hoy = date.today()
        if fecha > hoy:
            raise forms.ValidationError("La fecha de nacimiento no puede estar en el futuro.")
        if hoy.year - fecha.year > 110:
            raise forms.ValidationError("Revisa la fecha de nacimiento.")
        return fecha

    def save(self, commit=True):
        usuario = super().save(commit=False)
        # Entramos con el correo; el username interno es el mismo correo.
        usuario.username = self.cleaned_data["email"]
        usuario.rol = self.cleaned_data["rol"]
        usuario.acepta_tratamiento_datos = True
        usuario.fecha_autorizacion = timezone.now()
        if commit:
            usuario.save()
        return usuario


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Correo", widget=forms.EmailInput(attrs={"autofocus": True}))

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()
