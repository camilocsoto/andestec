# users/forms.py
from django import forms
from accounts.models import Usuario, Operador, TipoDocumento

class OperadorUpdateForm(forms.ModelForm):
    # Campos del modelo Usuario
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDocumento.objects.all(),
        label="Tipo de Documento",
        required=False
    )
    numDocumento = forms.CharField(label="Documento", required=False)
    estado = forms.BooleanField(label="Activo", required=False)

    class Meta:
        model = Operador
        fields = ["cargo"]  # solo cargo de Operador

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields["first_name"].initial = usuario.first_name
            self.fields["last_name"].initial = usuario.last_name
            self.fields["tipo_documento"].initial = usuario.tipo_documento
            self.fields["numDocumento"].initial = usuario.numDocumento
            self.fields["estado"].initial = usuario.estado

    def save(self, commit=True):
        operador = super().save(commit=False)
        usuario = operador.usuario

        usuario.first_name = self.cleaned_data["first_name"]
        usuario.last_name = self.cleaned_data["last_name"]
        usuario.tipo_documento = self.cleaned_data["tipo_documento"]
        usuario.numDocumento = self.cleaned_data["numDocumento"]
        usuario.estado = self.cleaned_data["estado"]

        if commit:
            usuario.save()
            operador.save()
        return operador
