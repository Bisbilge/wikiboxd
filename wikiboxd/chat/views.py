from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Conversation, Message
from .forms import MessageForm


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


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    if request.user not in conversation.participants.all():
        return redirect('chat:inbox')

    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    form = MessageForm()
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.conversation = conversation
            msg.sender = request.user
            msg.save()
            return redirect('chat:conversation', conversation_id=conversation.pk)

    messages_qs = conversation.messages.select_related('sender').all()
    other = conversation.participants.exclude(pk=request.user.pk).first()
    return render(request, 'chat/conversation.html', {
        'conversation': conversation,
        'messages_qs': messages_qs,
        'form': form,
        'other': other,
    })
