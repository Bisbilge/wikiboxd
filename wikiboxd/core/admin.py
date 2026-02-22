from django.contrib import admin
from .models import Article, Rating

# Makale (Article) modelinin admin panelindeki görünümünü özelleştiriyoruz.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # Admin panelindeki listede hangi sütunların görüneceğini belirler.
    list_display = ('title', 'author', 'created_at', 'updated_at')
    
    # Sağ tarafa bir filtreleme menüsü ekler (Örn: Yazar adına veya tarihe göre filtrele).
    list_filter = ('author', 'created_at')
    
    # Üst tarafa bir arama kutusu ekler. Sadece başlıkta ve içerikte arama yapar.
    search_fields = ('title', 'content')
    
    # Tarih alanlarını okunabilir yapıp, admin panelinde hiyerarşik bir tarih menüsü sunar.
    date_hierarchy = 'created_at'

# Puanlama (Rating) modelinin admin panelindeki görünümünü özelleştiriyoruz.
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    # Listede kullanıcıyı, makaleyi, verilen puanı ve tarihi yan yana gösterir.
    list_display = ('user', 'article', 'score', 'created_at')
    
    # Puanlara (1-10 arası) ve makalelere göre sağ taraftan filtreleme yapmayı sağlar.
    list_filter = ('score', 'article')
    
    # Kullanıcı adına ve makale başlığına göre arama yapabilmeyi sağlar.
    # user__username: User tablosundaki username sütununda ara demek.
    search_fields = ('user__username', 'article__title', 'review_text')