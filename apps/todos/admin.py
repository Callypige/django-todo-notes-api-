from django.contrib import admin
from .models import Todo

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'note', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']