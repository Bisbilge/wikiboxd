from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article


@receiver(post_save, sender=Article)
def notify_category_followers(sender, instance, created, **kwargs):
    if not created or not instance.category:
        return

    from users.models import Notification
    from django.contrib.auth.models import User


    cats = []
    cat = instance.category
    while cat:
        cats.append(cat)
        cat = cat.parent


    follower_ids = set()
    for c in cats:
        follower_ids.update(c.followers.values_list('id', flat=True))

    if instance.author_id:
        follower_ids.discard(instance.author_id)

    if not follower_ids:
        return

    category_name = instance.category.get_full_name()
    notifications = [
        Notification(
            user=follower,
            message=f'"{category_name}" kategorisine yeni makale eklendi: {instance.title}',
            article=instance,
        )
        for follower in User.objects.filter(pk__in=follower_ids)
    ]
    Notification.objects.bulk_create(notifications)
