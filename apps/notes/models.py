from django.db import models
from django.utils import timezone


class Note(models.Model):
    """
    A note is a piece of content that can be created, read, updated, and deleted.
    """
    objects = models.Manager()
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        return self.title

