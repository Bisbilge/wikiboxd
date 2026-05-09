def unread_notifications(request):
    if request.user.is_authenticated:
        notif_count = request.user.notifications.filter(is_read=False).count()
        request_count = request.user.received_follow_requests.count()
        from chat.models import Message
        chat_count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False,
        ).exclude(sender=request.user).count()
        return {
            'unread_notification_count': notif_count,
            'pending_follow_request_count': request_count,
            'unread_chat_count': chat_count,
        }
    return {
        'unread_notification_count': 0,
        'pending_follow_request_count': 0,
        'unread_chat_count': 0,
    }
