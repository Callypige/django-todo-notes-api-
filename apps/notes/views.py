from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from django.core.exceptions import ValidationError
from typing import Any

from .models import Note
from .serializers import NoteSerializer
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
    
    # Search by title and content
    search_fields = ['title', 'content']
    
    # Sorting by creation date, update date, title, status
    ordering_fields = ['created_at', 'updated_at', 'title', 'status']
    ordering = ['-created_at']  # Default: most recent first

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Override destroy to handle ValidationError from Note.delete().
        """
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response(
                {
                    "detail": str(e.message) if hasattr(e, 'message') else str(e),
                    "code": "note_has_todos",
                    "errors": {"note": [str(e.message) if hasattr(e, 'message') else str(e)]}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
