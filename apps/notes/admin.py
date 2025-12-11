from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'created_at', 'updated_at']
    search_fields = ['title', 'content']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']