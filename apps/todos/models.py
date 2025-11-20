from django.db import models
from django.utils import timezone

class TodoStatus(models.TextChoices):
    """Enum for the status of a todo"""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

class Todo(models.Model):
    """
    A todo is a task that can be created, read, updated, and deleted.
    """
    objects = models.Manager()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=TodoStatus.choices,
        default=TodoStatus.PENDING
    )
    note = models.ForeignKey(
        'notes.Note',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='todos'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.status}"
