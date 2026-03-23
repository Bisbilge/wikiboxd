from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.views.decorators.clickjacking import xframe_options_exempt
import requests
from .models import Article, Category
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
                headers={'User-Agent': 'Wikiboxd/1.0 (galatasaray-uni-project)'},
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

    headers = {'User-Agent': 'Wikiboxd/1.0 (galatasaray-uni-project)'}
    try:
        # Başlık için summary endpoint'i
        summary_resp = requests.get(
            f'https://tr.wikipedia.org/api/rest_v1/page/summary/{wiki_title}',
            headers=headers,
            timeout=5
        )
        if summary_resp.status_code != 200:
            messages.error(request, 'Makale Wikipedia\'da bulunamadı.')
            return redirect('articles:wiki_search')

        # Tam makale HTML'i için html endpoint'i
        html_resp = requests.get(
            f'https://tr.wikipedia.org/api/rest_v1/page/html/{wiki_title}',
            headers=headers,
            timeout=10
        )

        summary_data = summary_resp.json()
        title = summary_data['title']
        description = summary_data.get('extract', '')
        content = html_resp.text if html_resp.status_code == 200 else description

        article = Article.objects.create(
            title=title,
            description=description,
            content=content,
            wiki_url=wiki_url,
            author=request.user,
        )
        messages.success(request, f'"{article.title}" başarıyla eklendi!')
        return redirect('articles:detail', pk=article.pk)

    except requests.RequestException:
        messages.error(request, 'Wikipedia\'ya bağlanılamadı. Lütfen tekrar deneyin.')
        return redirect('articles:wiki_search')


@xframe_options_exempt
def wiki_embed_proxy(request, pk):
    from django.http import HttpResponse
    article = get_object_or_404(Article, pk=pk)

    if not article.wiki_url:
        return HttpResponse('<p>Wikipedia linki yok.</p>', content_type='text/html')

    wiki_title = article.wiki_url.split('/wiki/')[-1]
    headers = {'User-Agent': 'Wikiboxd/1.0 (galatasaray-uni-project)'}

    try:
        resp = requests.get(
            f'https://tr.wikipedia.org/api/rest_v1/page/html/{wiki_title}',
            headers=headers,
            timeout=10
        )
        html = resp.text
        # Göreli URL'leri Wikipedia'ya yönlendir
        html = html.replace('href="//', 'href="https://')
        html = html.replace('src="//', 'src="https://')
        html = html.replace('href="/', 'href="https://tr.wikipedia.org/')
        html = html.replace('src="/', 'src="https://tr.wikipedia.org/')
        # Wikipedia'nın temel stilini ekle
        style = '''
        <base target="_blank">
        <link rel="stylesheet" href="https://tr.wikipedia.org/w/load.php?modules=mediawiki.legacy.commonPrint,shared|mediawiki.skinning.elements|mediawiki.skinning.content|mediawiki.skinning.interface|skins.vector.styles&only=styles&skin=vector">
        <style>
            body { font-family: -apple-system, Linux Libertine, Georgia, serif; font-size: 14px; line-height: 1.7; padding: 1.5rem 2rem; color: #202122; background: #fff; }
            h1,h2,h3 { font-family: Linux Libertine, Georgia, serif; border-bottom: 1px solid #a2a9b1; }
            table { border-collapse: collapse; }
            td, th { border: 1px solid #a2a9b1; padding: 4px 8px; }
        </style>
        '''
        html = style + html
        return HttpResponse(html, content_type='text/html; charset=utf-8')
    except requests.RequestException:
        return HttpResponse('<p>Wikipedia\'ya bağlanılamadı.</p>', content_type='text/html')


def home(request):
    from ratings.models import Rating
    from comments.models import Comment
    from django.contrib.auth.models import User
    from django.db.models import Count

    articles_list = Article.objects.all().order_by('-created_at')

    # En çok puanlanan makaleler
    top_articles = Article.objects.annotate(
        rating_count=Count('ratings')
    ).filter(rating_count__gt=0).order_by('-rating_count')[:5]

    context = {
        'articles': articles_list,
        'top_articles': top_articles,
        'total_articles': articles_list.count(),
        'total_ratings': Rating.objects.count(),
        'total_users': User.objects.count(),
        'total_comments': Comment.objects.count(),
    }
    return render(request, 'index.html', context)

def article_list(request):
    articles = Article.objects.select_related('author', 'category').annotate(
        avg_score=Avg('ratings__score'),
        rating_count=Count('ratings'),
    )

    # --- Filtreleme ---
    q = request.GET.get('q', '').strip()
    category_slug = request.GET.get('kategori', '').strip()
    sort = request.GET.get('siralama', 'yeni')

    if q:
        articles = articles.filter(Q(title__icontains=q) | Q(content__icontains=q))

    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()
        if selected_category:
            # Seçilen kategori veya alt kategorileri
            sub_ids = list(selected_category.subcategories.values_list('id', flat=True))
            cat_ids = [selected_category.id] + sub_ids
            articles = articles.filter(category_id__in=cat_ids)

    # --- Sıralama ---
    sort_options = {
        'yeni': '-created_at',
        'eski': 'created_at',
        'puan': '-avg_score',
        'puan_sayisi': '-rating_count',
    }
    articles = articles.order_by(sort_options.get(sort, '-created_at'))

    # Sidebar için tüm ana kategoriler
    categories = Category.objects.filter(parent=None).prefetch_related('subcategories').annotate(
        article_count=Count('articles')
    )

    context = {
        'articles': articles,
        'categories': categories,
        'selected_category': selected_category,
        'q': q,
        'sort': sort,
    }
    return render(request, 'articles/article_list.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    sub_ids = list(category.subcategories.values_list('id', flat=True))
    cat_ids = [category.id] + sub_ids
    articles = Article.objects.filter(category_id__in=cat_ids).select_related('author', 'category').annotate(
        avg_score=Avg('ratings__score'),
        rating_count=Count('ratings'),
    ).order_by('-created_at')
    subcategories = category.subcategories.annotate(article_count=Count('articles'))
    context = {
        'category': category,
        'articles': articles,
        'subcategories': subcategories,
    }
    return render(request, 'articles/category_detail.html', context)


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