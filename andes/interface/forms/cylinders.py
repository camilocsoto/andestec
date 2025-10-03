# forms.py
from django import forms
from interface.models import CaracteristicasCilindro, ComposicionGas, GasRestante

class CaracteristicasCilindroForm(forms.ModelForm):
    # Foraneas como ModelChoiceField (ChoiceField semántico)
    GasRestante = forms.ModelChoiceField(
        queryset=GasRestante.objects.all(),
        required=False,
        label="Gas restante",
        empty_label="(sin sensor asociado)",
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 rounded border'})
    )
    ComposicionGas = forms.ModelChoiceField(
        queryset=ComposicionGas.objects.all(),
        required=False,
        label="Composición del gas",
        empty_label="(sin composición)",
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 rounded border'})
    )

    class Meta:
        model = CaracteristicasCilindro
        # orden de campos pedido: nombre, gas restante, composicion gas, notas, ...resto
        fields = [
            'nombre',
            'GasRestante',
            'ComposicionGas',
            'notas',
            'volumen_interno_m3',
            'masa_cil_vacio_kg',
            'masa_cil_lleno_kg',
            'masa_gas_restant_kg',
            'coef_descarga_cd',
            'diametro_orificio_m',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border', 'placeholder': 'Nombre identificador'}),
            'notas': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border', 'placeholder': 'Notas o referencia (opcional)'}),
            'volumen_interno_m3': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded border', 'step': 'any', 'placeholder': 'm3'}),
            'masa_cil_vacio_kg': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded border', 'step': 'any', 'placeholder': 'Kg'}),
            'masa_cil_lleno_kg': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded border', 'step': 'any', 'placeholder': 'Kg'}),
            'masa_gas_restant_kg': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded border', 'step': 'any', 'placeholder': 'Kg'}),
            'coef_descarga_cd': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded border', 'step': 'any', 'placeholder': 'cd'}),
            'diametro_orificio_m': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded border', 'step': 'any', 'placeholder': 'm'}),
        }
        labels = {
            'nombre': 'Nombre',
            'notas': 'Notas',
            'volumen_interno_m3': 'Volumen interno (m³)',
            'masa_cil_vacio_kg': 'Masa cilindro vacío (Kg)',
            'masa_cil_lleno_kg': 'Masa cilindro lleno (Kg)',
            'masa_gas_restant_kg': 'Cant. gas restante (Kg)',
            'coef_descarga_cd': 'Coeficiente de descarga (cd)',
            'diametro_orificio_m': 'Diámetro de orificio (m)',
        }
