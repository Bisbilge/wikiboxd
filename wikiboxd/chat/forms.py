from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Mesaj yaz...',
                'class': 'form-control',
                'style': 'resize: none; border-radius: 2px 0 0 2px;',
            }),
        }
        labels = {'body': ''}
