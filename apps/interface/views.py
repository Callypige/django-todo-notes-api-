from django.views.generic import ListView
from apps.notes.models import Note
from apps.todos.models import Todo


class HomeView(ListView):
    model = Note
    template_name = 'interface/home.html'
    context_object_name = 'notes'
    
    def get_queryset(self):
        # Associate each note with its todos to minimize DB queries
        return Note.objects.prefetch_related('todos').all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add orphan todos (todos without a note) to the context
        context['orphan_todos'] = Todo.objects.filter(note__isnull=True)
        return context
