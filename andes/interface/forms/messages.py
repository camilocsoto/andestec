from django import forms
from interface.models import Mensaje

class MessageForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['mensajes']  # solo la caja de texto
        widgets = {
            'mensajes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Escribe tu comentario aquí...',
                'class': 'w-full border rounded p-2'
            }),
        }
        labels = {
            'mensajes': ''
        }
