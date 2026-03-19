from django.contrib import admin
from .models import Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'score', 'created_at')
    list_filter = ('score',)
    search_fields = ('user__username', 'article__title')
    date_hierarchy = 'created_at'
