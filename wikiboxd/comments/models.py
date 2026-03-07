from django.db import models
from django.contrib.auth.models import User
from articles.models import Article # Hangi makaleye yorum yapıldığını bilmek için

class Comment(models.Model):
    # Bir makale silinirse, altındaki yorumlar da silinsin (CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    
    # Bir kullanıcı silinirse, yaptığı yorumlar da silinsin
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    
    # Yorumun içeriği
    text = models.TextField()
    
    # Tarih bilgileri
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Kullanıcı yorumunu düzenlerse diye

    def __str__(self):
        return f"{self.user.username} kullanıcısının {self.article.title} makalesine yorumu"