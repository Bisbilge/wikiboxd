from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article


@receiver(post_save, sender=Article)
def notify_category_followers(sender, instance, created, **kwargs):
    if not created or not instance.category:
        return

    from users.models import Notification

    category = instance.category
    followers = category.followers.exclude(pk=instance.author_id) if instance.author_id else category.followers.all()

    notifications = [
        Notification(
            user=follower,
            message=f'"{category.name}" kategorisine yeni makale eklendi: {instance.title}',
            article=instance,
        )
        for follower in followers
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)
