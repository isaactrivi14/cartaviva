from django import forms

from .models import Evento


class EventoForm(forms.ModelForm):
    """
    ModelForm del CRUD. Las reglas de negocio están en Evento.clean(), que Django
    llama automáticamente al validar el formulario en el servidor.
    """

    class Meta:
        model = Evento
        fields = [
            "titulo", "categoria", "descripcion", "es_relampago", "fecha_inicio", "fecha_fin",
            "direccion", "barrio", "latitud", "longitud", "cupo_maximo", "solo_mayores_18",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "fecha_inicio": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "fecha_fin": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "latitud": forms.NumberInput(attrs={"step": "0.000001"}),
            "longitud": forms.NumberInput(attrs={"step": "0.000001"}),
        }
        labels = {"titulo": "Título", "descripcion": "Descripción", "direccion": "Dirección", "cupo_maximo": "Cupo máximo"}
        help_texts = {
            "es_relampago": "Convocatoria espontánea: debe durar entre 1 y 6 horas.",
            "latitud": "Toca el mapa para elegir el punto.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in ("fecha_inicio", "fecha_fin"):
            self.fields[campo].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean_titulo(self):
        titulo = self.cleaned_data["titulo"].strip()
        if len(titulo) < 5:
            raise forms.ValidationError("El título debe tener al menos 5 caracteres.")
        return titulo
