from django.db import models
from django.core.exceptions import ValidationError

from apps.core.models import TimestampedModel


class NoteStatus(models.TextChoices):
    """Enum for the status of a note"""
    ACTIVE = 'active', 'Active'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    ARCHIVED = 'archived', 'Archived'


class Note(TimestampedModel):
    """
    A note is a piece of content that can be created, read, updated, and deleted.
    """
    objects = models.Manager()
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    status = models.CharField(
        max_length=20,
        choices=NoteStatus.choices,
        default=NoteStatus.ACTIVE,
        help_text="Status automatically updated based on associated todos"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self) -> str:

        return self.title

    def delete(self, *args, **kwargs) -> None:
        """
        Prevent deletion if this note has associated todos.
        Raises ValidationError if todos exist.
        """
        todos_count = getattr(self, 'todos', None)
        if todos_count and todos_count.exists():
            count = todos_count.count()
            raise ValidationError(
                f"Cannot delete note '{self.title}' because it has {count} associated todo(s). "
                "Please delete or unlink the todos first."
            )
        super().delete(*args, **kwargs)

    def update_status_from_todos(self) -> bool:
        """
        Automatically update the note's status based on associated todos:
        - COMPLETED: if all todos are completed
        - IN_PROGRESS: if at least one todo is in progress
        - ACTIVE: if there are pending todos
        - ARCHIVED: no change if already archived (manual status)
        
        Returns True if status was changed, False otherwise.
        """
        # Don't auto-update archived notes
        if self.status == NoteStatus.ARCHIVED:
            return False

        # Import TodoStatus here to avoid circular import
        from apps.todos.models import TodoStatus
        
        todos = getattr(self, 'todos', None)
        if not todos:
            return False
        
        # No todos associated - reset to ACTIVE
        if not todos.exists():
            return self._update_status(NoteStatus.ACTIVE)
        
        # Determine new status based on todo statuses
        todo_statuses = todos.values_list('status', flat=True)
        
        if all(status == TodoStatus.COMPLETED for status in todo_statuses):
            new_status = NoteStatus.COMPLETED
        elif TodoStatus.IN_PROGRESS in todo_statuses:
            new_status = NoteStatus.IN_PROGRESS
        else:
            new_status = NoteStatus.ACTIVE

        return self._update_status(new_status)
    
    def _update_status(self, new_status: str) -> bool:
        """Helper method to update status if changed."""
        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False