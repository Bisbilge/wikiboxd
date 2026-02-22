from django.shortcuts import render
from .models import Article

def home(request):
    # Veritabanındaki tüm makaleleri oluşturulma tarihine göre en yeniler üstte olacak şekilde çekiyoruz
    articles = Article.objects.all().order_by('-created_at')
    
    # context sözlüğü ile bu veriyi index.html şablonuna yolluyoruz
    context = {
        'articles': articles
    }
    return render(request, 'index.html', context)