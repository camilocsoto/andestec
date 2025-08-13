from django import forms
from models import Empresa, TipoDocumento, Rol
from typing import cast

class EmpresaRegistroForm(forms.ModelForm):
    # Campo extra para natural / jurídica
    TIPO_PERSONA_CHOICES = [
        ('natural', 'Natural'),
        ('jurídica', 'Jurídica'),
    ]
    tipo_persona = forms.ChoiceField(choices=TIPO_PERSONA_CHOICES, label="Tipo de Persona")

    # Campo de tipo documento filtrado (inicialmente vacío, lo llenamos luego)
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDocumento.objects.none(),
        label="Tipo de Documento"
    )

    email = forms.EmailField(label="Correo")
    numDocumento = forms.CharField(max_length=45, required=False)
    rol = forms.ModelChoiceField(queryset=Rol.objects.all())

    class Meta:
        model = Empresa
        fields = ['tipo_persona', 'tipo_documento', 'numDocumento', 'email', 'rol', 'cantidadOperarios', 'direccion']

    def __init__(self, *args, **kwargs):
        tipo_persona_seleccionada = None
        if 'data' in kwargs:  # Si viene de POST
            tipo_persona_seleccionada = kwargs['data'].get('tipo_persona')
        super().__init__(*args, **kwargs)

        if tipo_persona_seleccionada:
            tipo_documento_field = cast(forms.ModelChoiceField, self.fields['tipo_documento'])
            tipo_documento_field.queryset = TipoDocumento.objects.filter(
            tipoPersona=tipo_persona_seleccionada
        )