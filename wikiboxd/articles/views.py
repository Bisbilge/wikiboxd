from django.shortcuts import render
from .models import Article

def home(request):
    # Veritabanındaki tüm makaleleri en yeniler üstte olacak şekilde çekiyoruz
    articles_list = Article.objects.all().order_by('-created_at')
    
    context = {
        'articles': articles_list
    }
    return render(request, 'index.html', context)