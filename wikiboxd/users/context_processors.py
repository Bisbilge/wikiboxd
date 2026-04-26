def unread_notifications(request):
    if request.user.is_authenticated:
        notif_count = request.user.notifications.filter(is_read=False).count()
        request_count = request.user.received_follow_requests.count()
        return {
            'unread_notification_count': notif_count,
            'pending_follow_request_count': request_count,
        }
    return {'unread_notification_count': 0, 'pending_follow_request_count': 0}
