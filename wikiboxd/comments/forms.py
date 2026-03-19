from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Yorumunuzu buraya yazın...'}),
        label='Yorum'
    )

    class Meta:
        model = Comment
        fields = ['text']
