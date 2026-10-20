from django.contrib import admin

from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'director', 'year', 'genre', 'rating', 'created_at')
    list_filter = ('genre', 'year')
    search_fields = ('title', 'director', 'genre')
    ordering = ('-created_at',)
