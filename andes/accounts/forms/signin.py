from django import forms
from typing import cast
from accounts.models import Empresa, TipoDocumento, Rol

class EmpresaRegistroForm(forms.ModelForm):
    TIPO_PERSONA_CHOICES = [
        ('natural', 'Natural'),
        ('jurídica', 'Jurídica'),
    ]
    
    tipo_persona = forms.ChoiceField(choices=TIPO_PERSONA_CHOICES, label="Tipo de Persona")
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)

    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDocumento.objects.none(),
        label="Tipo de documento"
    )
    numDocumento = forms.CharField(label="Número de documento", max_length=45)
    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Empresa
        fields = [
            'first_name',
            'last_name',
            'tipo_persona',
            'tipo_documento',
            'numDocumento',
            'direccion',
            'email',
            'password',
            'password_confirm',
            
        ]

    def __init__(self, *args, **kwargs):
        tipo_persona_seleccionada = None
        if 'data' in kwargs:
            tipo_persona_seleccionada = kwargs['data'].get('tipo_persona')
        super().__init__(*args, **kwargs)

        # Rol fijo
        self.instance.rol = cast(Rol, Rol.objects.get(pk=2))

        # Filtrar documentos
        if tipo_persona_seleccionada:
            tipo_documento_field = cast(forms.ModelChoiceField, self.fields['tipo_documento'])
            tipo_documento_field.queryset = TipoDocumento.objects.filter(
                tipoPersona=tipo_persona_seleccionada
            )

            # Si es jurídica, ocultar last_name
            if tipo_persona_seleccionada == "jurídica":
                self.fields['last_name'].required = False
                self.fields['last_name'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden")

        return cleaned_data
