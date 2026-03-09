from django.db import models
from django.contrib.auth.models import User
from articles.models import Article 
class Comment(models.Model):

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    
    text = models.TextField()
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.user.username} kullanıcısının {self.article.title} makalesine yorumu"