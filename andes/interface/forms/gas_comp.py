from django import forms
from interface.models import ComposicionGas

class ComposicionGasForm(forms.ModelForm):
    class Meta:
        model = ComposicionGas
        fields = ['nombre', 'descripcion', 'masa_molar', 'y_entropia', 'z_factor', 'densidad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border', 'placeholder': 'Nombre del gas'}),
            'descripcion': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border', 'placeholder': 'Descripción corta'}),
            'masa_molar': forms.NumberInput(attrs={'step': 'any', 'class': 'w-full px-3 py-2 rounded border', 'placeholder': 'Masa molar'}),
            'y_entropia': forms.NumberInput(attrs={'step': 'any', 'class': 'w-full px-3 py-2 rounded border', 'placeholder': 'Y entropía'}),
            'z_factor': forms.NumberInput(attrs={'step': 'any', 'class': 'w-full px-3 py-2 rounded border', 'placeholder': 'Z factor'}),
            'densidad': forms.NumberInput(attrs={'step': 'any', 'class': 'w-full px-3 py-2 rounded border', 'placeholder': 'Densidad'}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'masa_molar': 'Masa molar [g/mol]',
            'y_entropia': 'Y entropía',
            'z_factor': 'Z factor',
            'densidad': 'Densidad [kg/m3 | g/L]',
        }