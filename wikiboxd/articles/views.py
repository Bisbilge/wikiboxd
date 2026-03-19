from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
import requests
from .models import Article
from comments.forms import CommentForm

@login_required
def wiki_search(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        try:
            response = requests.get(
                'https://tr.wikipedia.org/w/api.php',
                params={
                    'action': 'query',
                    'list': 'search',
                    'srsearch': query,
                    'format': 'json',
                    'srlimit': 10,
                },
                timeout=5
            )
            data = response.json()
            results = data.get('query', {}).get('search', [])
        except requests.RequestException:
            messages.error(request, 'Wikipedia\'ya bağlanılamadı. Lütfen tekrar deneyin.')

    return render(request, 'articles/wiki_search.html', {'results': results, 'query': query})


@login_required
def wiki_import(request, wiki_title):
    wiki_url = f'https://tr.wikipedia.org/wiki/{wiki_title}'

    # Makale zaten DB'de varsa direkt oraya yönlendir
    existing = Article.objects.filter(wiki_url=wiki_url).first()
    if existing:
        return redirect('articles:detail', pk=existing.pk)

    try:
        response = requests.get(
            f'https://tr.wikipedia.org/api/rest_v1/page/summary/{wiki_title}',
            timeout=5
        )
        if response.status_code != 200:
            messages.error(request, 'Makale Wikipedia\'da bulunamadı.')
            return redirect('articles:wiki_search')

        data = response.json()
        article = Article.objects.create(
            title=data['title'],
            content=data.get('extract', ''),
            wiki_url=wiki_url,
            author=request.user,
        )
        messages.success(request, f'"{article.title}" başarıyla eklendi!')
        return redirect('articles:detail', pk=article.pk)

    except requests.RequestException:
        messages.error(request, 'Wikipedia\'ya bağlanılamadı. Lütfen tekrar deneyin.')
        return redirect('articles:wiki_search')


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

    comments = article.comments.select_related('user').order_by('-created_at')

    context = {
        'article': article,
        'ratings': ratings,
        'avg_score': avg_score,
        'user_rating': user_rating,
        'comments': comments,
        'comment_form': CommentForm(),
    }
    return render(request, 'articles/article_detail.html', context)