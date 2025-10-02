from django import forms
from interface.models import TipoSensor

class TipoSensorForm(forms.ModelForm):
    class Meta:
        model = TipoSensor
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded border',
                'placeholder': 'Nombre del tipo de sensor'
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded border',
                'placeholder': 'Descripción'
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
        }