from rest_framework import viewsets

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
