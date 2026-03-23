from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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

# Profil Görünümü (kendi profili)
@login_required
def profile(request):
    user_articles = request.user.articles.all()
    user_ratings = request.user.ratings.all()
    followed_categories = request.user.followed_categories.all()
    following = request.user.profile.following.all()
    followers = request.user.followers.all()

    context = {
        'user_articles': user_articles,
        'user_ratings': user_ratings,
        'followed_categories': followed_categories,
        'following': following,
        'followers': followers,
    }
    return render(request, 'users/profile.html', context)


# Herkese açık kullanıcı profili
def user_profile(request, username):
    viewed_user = get_object_or_404(User, username=username)
    if request.user == viewed_user:
        return redirect('users:profile')

    Profile.objects.get_or_create(user=viewed_user)

    is_following = (
        request.user.is_authenticated and
        viewed_user in request.user.profile.following.all()
    )
    context = {
        'viewed_user': viewed_user,
        'user_articles': viewed_user.articles.all(),
        'user_ratings': viewed_user.ratings.all(),
        'following': viewed_user.profile.following.all(),
        'followers': viewed_user.followers.all(),
        'is_following': is_following,
    }
    return render(request, 'users/user_profile.html', context)


# Takip et / bırak
@login_required
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return redirect('users:user_profile', username=username)

    profile = request.user.profile
    if target in profile.following.all():
        profile.following.remove(target)
    else:
        profile.following.add(target)
    return redirect('users:user_profile', username=username)

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