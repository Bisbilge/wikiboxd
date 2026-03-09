from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

# Kayıt Olma Formu
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='E-posta Adresi')
    first_name = forms.CharField(max_length=30, required=False, label='Ad')
    last_name = forms.CharField(max_length=30, required=False, label='Soyad')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

# Kullanıcı Ana Bilgileri Düzenleme Formu
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='E-posta Adresi')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

# Profil (Ekstra Bilgiler) Düzenleme Formu
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']