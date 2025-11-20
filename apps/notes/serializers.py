from rest_framework import serializers
from .models import Note

class NoteSerializer(serializers.ModelSerializer):
    todos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = ["id", "title", "content", "status", "todos_count", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "todos_count", "created_at", "updated_at"]
    
    def get_todos_count(self, obj):
        """Return the number of todos associated with this note."""
        return obj.todos.count() if hasattr(obj, 'todos') else 0