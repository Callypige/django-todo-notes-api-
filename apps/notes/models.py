from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class NoteStatus(models.TextChoices):
    """Enum for the status of a note"""
    ACTIVE = 'active', 'Active'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    ARCHIVED = 'archived', 'Archived'


class Note(models.Model):
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
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """
        Prevent deletion if this note has associated todos.
        Raises ValidationError if todos exist.
        """
        if self.todos.exists():
            raise ValidationError(
                f"Cannot delete note '{self.title}' because it has {self.todos.count()} associated todo(s). "
                "Please delete or unlink the todos first."
            )
        super().delete(*args, **kwargs)

    def update_status_from_todos(self):
        """
        Automatically update the note's status based on associated todos:
        - COMPLETED: if all todos are completed
        - IN_PROGRESS: if at least one todo is in progress
        - ACTIVE: if there are pending todos
        - ARCHIVED: no change if already archived (manual status)
        """
        # Don't auto-update archived notes
        if self.status == NoteStatus.ARCHIVED:
            return False

        todos = self.todos.all()
        
        # No todos associated
        if not todos.exists():
            if self.status != NoteStatus.ACTIVE:
                self.status = NoteStatus.ACTIVE
                self.save(update_fields=['status', 'updated_at'])
                return True
            return False

        # Import TodoStatus here to avoid circular import
        from apps.todos.models import TodoStatus
        
        todo_statuses = list(todos.values_list('status', flat=True))
        
        # All todos completed
        if all(s == TodoStatus.COMPLETED for s in todo_statuses):
            new_status = NoteStatus.COMPLETED
        # At least one in progress
        elif TodoStatus.IN_PROGRESS in todo_statuses:
            new_status = NoteStatus.IN_PROGRESS
        # Has pending todos
        else:
            new_status = NoteStatus.ACTIVE

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status', 'updated_at'])
            return True
        
        return False

