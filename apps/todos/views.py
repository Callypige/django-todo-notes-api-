from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Todo
from .serializers import TodoSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(tags=['Todos'])
@extend_schema_view(
    list=extend_schema(summary='List all todos'),
    retrieve=extend_schema(summary='Get a todo by ID'),
    create=extend_schema(summary='Create a new todo'),
    update=extend_schema(summary='Update a todo by ID'),
    destroy=extend_schema(summary='Delete a todo by ID'),
)   
class TodoViewSet(viewsets.ModelViewSet):
    """Viewset for the Todo model."""

    queryset = Todo.objects.select_related("note").all()
    serializer_class = TodoSerializer

    @action(detail=False, methods=["get"], url_path="by-note")
    @extend_schema(summary="List todos linked to a note", description="Return all todos attached to the given note id.")
    def by_note(self, request):
        """Return todos filtered by note id."""
        note_param = request.query_params.get("note")
        if note_param is None:
            return Response(
                {
                    "detail": "Query parameter 'note' is required.",
                    "code": "missing_note_param",
                    "errors": {"note": ["This query parameter is required."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            note_id = int(note_param)
        except (TypeError, ValueError):
            return Response(
                {
                    "detail": "Query parameter 'note' must be an integer.",
                    "code": "invalid_note_param",
                    "errors": {"note": ["This query parameter must be an integer."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        todos = self.get_queryset().filter(note_id=note_id)
        serializer = self.get_serializer(todos, many=True)
        return Response(serializer.data)
