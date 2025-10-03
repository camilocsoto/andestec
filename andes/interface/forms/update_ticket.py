from django import forms

class EstadoTicketForm(forms.Form):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_proceso', 'En proceso'),
        ('cerrado', 'Cerrado'),
    ]
    estado = forms.ChoiceField(choices=ESTADO_CHOICES, label="Nuevo estado")