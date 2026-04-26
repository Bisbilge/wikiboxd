from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile, Notification, FollowRequest

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
    followers = User.objects.filter(profile__following=request.user)
    favorite_articles = request.user.profile.favorite_articles.all()
    incoming_requests = request.user.received_follow_requests.select_related('from_user').all()

    context = {
        'user_articles': user_articles,
        'user_ratings': user_ratings,
        'followed_categories': followed_categories,
        'following': following,
        'followers': followers,
        'favorite_articles': favorite_articles,
        'incoming_requests': incoming_requests,
    }
    return render(request, 'users/profile.html', context)


# Herkese açık kullanıcı profili
def user_profile(request, username):
    viewed_user = get_object_or_404(User, username=username)
    if request.user == viewed_user:
        return redirect('users:profile')

    profile, _ = Profile.objects.get_or_create(user=viewed_user)

    is_following = (
        request.user.is_authenticated and
        viewed_user in request.user.profile.following.all()
    )

    has_pending_request = (
        request.user.is_authenticated and
        FollowRequest.objects.filter(from_user=request.user, to_user=viewed_user).exists()
    )

    if profile.is_private and not is_following:
        return render(request, 'users/private_profile.html', {
            'viewed_user': viewed_user,
            'is_following': is_following,
            'has_pending_request': has_pending_request,
        })

    context = {
        'viewed_user': viewed_user,
        'user_articles': viewed_user.articles.all(),
        'user_ratings': viewed_user.ratings.all(),
        'following': viewed_user.profile.following.all(),
        'followers': User.objects.filter(profile__following=viewed_user),
        'is_following': is_following,
        'has_pending_request': has_pending_request,
    }
    return render(request, 'users/user_profile.html', context)


# Takip edilenler listesi
def following_list(request, username):
    viewed_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=viewed_user)

    if profile.is_private and not (
        request.user.is_authenticated and viewed_user in request.user.profile.following.all()
    ) and request.user != viewed_user:
        return redirect('users:user_profile', username=username)

    following = profile.following.all()
    pending_ids = set(
        FollowRequest.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
    ) if request.user.is_authenticated else set()
    context = {
        'viewed_user': viewed_user,
        'user_list': following,
        'list_type': 'following',
        'pending_request_ids': pending_ids,
    }
    return render(request, 'users/follow_list.html', context)


# Takipçiler listesi
def followers_list(request, username):
    viewed_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=viewed_user)

    if profile.is_private and not (
        request.user.is_authenticated and viewed_user in request.user.profile.following.all()
    ) and request.user != viewed_user:
        return redirect('users:user_profile', username=username)

    followers = User.objects.filter(profile__following=viewed_user)
    pending_ids = set(
        FollowRequest.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
    ) if request.user.is_authenticated else set()
    context = {
        'viewed_user': viewed_user,
        'user_list': followers,
        'list_type': 'followers',
        'pending_request_ids': pending_ids,
    }
    return render(request, 'users/follow_list.html', context)


# Bildirimler
@login_required
def notifications_list(request):
    notifications = request.user.notifications.select_related('article').all()
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'users/notifications.html', {'notifications': notifications})


# Kullanıcı arama
def user_search(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        results = User.objects.filter(username__icontains=q).exclude(
            pk=request.user.pk if request.user.is_authenticated else None
        ).select_related('profile')

    pending_ids = set(
        FollowRequest.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
    ) if request.user.is_authenticated else set()

    return render(request, 'users/user_search.html', {
        'results': results,
        'q': q,
        'pending_request_ids': pending_ids,
    })


# Takip isteği gönder / iptal et / takipten çık
@login_required
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return redirect('users:user_profile', username=username)

    profile = request.user.profile

    if target in profile.following.all():
        # Zaten takip ediyorsa → takipten çık
        profile.following.remove(target)
    else:
        existing_request = FollowRequest.objects.filter(from_user=request.user, to_user=target).first()
        if existing_request:
            # Bekleyen istek varsa → iptal et
            existing_request.delete()
        else:
            # İstek yok → yeni istek gönder
            FollowRequest.objects.get_or_create(from_user=request.user, to_user=target)

    return redirect('users:user_profile', username=username)


# Takip isteğini kabul et veya reddet
@login_required
def handle_follow_request(request, request_id, action):
    follow_request = get_object_or_404(FollowRequest, pk=request_id, to_user=request.user)

    if action == 'kabul':
        follow_request.from_user.profile.following.add(request.user)
        follow_request.delete()
        messages.success(request, f'{follow_request.from_user.username} artık seni takip ediyor.')
    elif action == 'reddet':
        follow_request.delete()

    return redirect('users:profile')

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