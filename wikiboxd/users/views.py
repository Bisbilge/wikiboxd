from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm

# Kayıt Olma Görünümü
def register(request):
    if request.user.is_authenticated:
        return redirect('articles:home') # Zaten giriş yapmışsa anasayfaya at
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save() # Kullanıcıyı veritabanına kaydet
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hesabın oluşturuldu {username}! Şimdi giriş yapabilirsin.')
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

# Profil Görünümü (Sadece giriş yapmış kullanıcılar görebilir)
@login_required
def profile(request):
    # Kullanıcının makalelerini ve yorumlarını template'e gönderebiliriz
    user_articles = request.user.articles.all()
    user_ratings = request.user.ratings.all()
    
    context = {
        'user_articles': user_articles,
        'user_ratings': user_ratings
    }
    return render(request, 'users/profile.html', context)

# Profil Düzenleme Görünümü
@login_required
def edit_profile(request):
    if request.method == 'POST':
        # formun içine request.user vererek mevcut bilgilerin formda dolu gelmesini sağlıyoruz
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profilin başarıyla güncellendi!')
            return redirect('users:profile')
    else:
        form = UserUpdateForm(instance=request.user)
        
    return render(request, 'users/edit_profile.html', {'form': form})