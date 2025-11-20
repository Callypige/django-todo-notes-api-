from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Note
from .serializers import NoteSerializer
from apps.todos.models import Todo
from apps.todos.serializers import TodoSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(tags=['Notes'])
@extend_schema_view(
    list=extend_schema(summary='List all notes'),
    retrieve=extend_schema(summary='Get a note by ID'),
    create=extend_schema(summary='Create a new note'),
    update=extend_schema(summary='Update a note by ID'),
    destroy=extend_schema(summary='Delete a note by ID'),
)
class NoteViewSet(viewsets.ModelViewSet):
    """Viewset for the Note model."""

    queryset = Note.objects.prefetch_related("todos").all()
    serializer_class = NoteSerializer

    @action(detail=True, methods=['get'])
    @extend_schema(summary='Get the todos for a note')
    def get_todos(self, request, pk=None):
        """Return the todos for a note."""
        note = self.get_queryset().get(pk=pk)
        todos = Todo.objects.filter(note=note)
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)
