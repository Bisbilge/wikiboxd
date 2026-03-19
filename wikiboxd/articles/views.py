from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from .models import Article

def home(request):
    # Veritabanındaki tüm makaleleri en yeniler üstte olacak şekilde çekiyoruz
    articles_list = Article.objects.all().order_by('-created_at')

    context = {
        'articles': articles_list
    }
    return render(request, 'index.html', context)

def detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    ratings = article.ratings.select_related('user').order_by('-created_at')
    avg_score = ratings.aggregate(avg=Avg('score'))['avg']

    user_rating = None
    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()

    context = {
        'article': article,
        'ratings': ratings,
        'avg_score': avg_score,
        'user_rating': user_rating,
    }
    return render(request, 'articles/article_detail.html', context)