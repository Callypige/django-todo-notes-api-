from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from typing import Any

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

    def __str__(self) -> str:
        return f"{self.title} - {self.status}"


@receiver(post_save, sender=Todo)
def update_note_status_on_todo_save(sender: type[Todo], instance: Todo, **kwargs: Any) -> None:
    """
    Signal to update the note's status when a todo is created or updated.
    """
    if instance.note:
        instance.note.update_status_from_todos()


@receiver(post_delete, sender=Todo)
def update_note_status_on_todo_delete(sender: type[Todo], instance: Todo, **kwargs: Any) -> None:
    """
    Signal to update the note's status when a todo is deleted.
    """
    if instance.note:
        instance.note.update_status_from_todos()
