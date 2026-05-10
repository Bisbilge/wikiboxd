from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'participant_list')
    filter_horizontal = ('participants',)

    def participant_list(self, obj):
        return ', '.join(u.username for u in obj.participants.all())
    participant_list.short_description = 'Katılımcılar'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'body_preview', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('sender__username', 'body')

    def body_preview(self, obj):
        return obj.body[:60]
    body_preview.short_description = 'Mesaj'
