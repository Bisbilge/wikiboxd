from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from articles.models import Article
from .models import Rating
from .forms import RatingForm

@login_required
def rate_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Kullanıcı bu makaleye daha önce puan verdi mi?
    existing_rating = Rating.objects.filter(user=request.user, article=article).first()
    if existing_rating:
        messages.warning(request, 'Bu makaleye zaten puan verdiniz.')
        return redirect('articles:detail', pk=pk)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.article = article
            rating.save()
            messages.success(request, 'Puanınız başarıyla kaydedildi!')

    return redirect('articles:detail', pk=pk)
