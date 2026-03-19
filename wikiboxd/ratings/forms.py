from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    score = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'placeholder': '1-10 arası puan girin'}),
        label='Puan (1-10)'
    )
    review_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Yorumunuzu buraya yazın (opsiyonel)...'}),
        label='Yorum'
    )

    class Meta:
        model = Rating
        fields = ['score', 'review_text']
