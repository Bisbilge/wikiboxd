from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile

# Kayıt Olma Görünümü
def register(request):
    if request.user.is_authenticated:
        return redirect('articles:home')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save() 
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hesabın oluşturuldu {username}! Şimdi giriş yapabilirsin.')
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

# Profil Görünümü
@login_required
def profile(request):
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
    # Eski kayıtlı kullanıcıların profili henüz veritabanında yoksa hatayı önlemek için:
    Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profilin başarıyla güncellendi!')
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/edit_profile.html', context)