from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Conversation, Message


@login_required
def inbox(request):
    conversations = request.user.conversations.prefetch_related('participants', 'messages').all()
    conv_data = []
    for conv in conversations:
        other = conv.participants.exclude(pk=request.user.pk).first()
        last = conv.messages.last()
        unread = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
        conv_data.append({'conv': conv, 'other': other, 'last': last, 'unread': unread})
    return render(request, 'chat/inbox.html', {'conv_data': conv_data})
