from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, verbose_name="Biyografi")
    is_private = models.BooleanField(default=False, verbose_name="Gizli Profil")
    following = models.ManyToManyField(
        User,
        related_name='followers',
        blank=True,
        verbose_name='Takip Edilenler'
    )
    favorite_articles = models.ManyToManyField(
        'articles.Article',
        related_name='favorited_by',
        blank=True,
        verbose_name='Favori Makaleler'
    )

    def __str__(self):
        return f"{self.user.username} Profili"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=300)
    article = models.ForeignKey(
        'articles.Article',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.message[:50]}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()