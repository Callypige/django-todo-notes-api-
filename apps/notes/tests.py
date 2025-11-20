from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from django.core.exceptions import ValidationError

from .models import Note, NoteStatus
from apps.todos.models import Todo, TodoStatus


class NoteModelTest(TestCase):
    """Tests for the Note model"""

    def test_create_note(self):
        """Test the creation of a note"""
        note = Note.objects.create(
            title="Test Note",
            content="Contenu de test"
        )
        self.assertEqual(note.title, "Test Note")
        self.assertEqual(note.content, "Contenu de test")
        self.assertIsNotNone(note.created_at)
        self.assertIsNotNone(note.updated_at)

    def test_note_str(self):
        """Test the __str__ method"""
        note = Note.objects.create(title="Ma Note")
        self.assertEqual(str(note), "Ma Note")

    def test_note_ordering(self):
        """Test the ordering by creation date"""
        note1 = Note.objects.create(title="Note 1", content="Content 1")
        note2 = Note.objects.create(title="Note 2", content="Content 2")
        notes = list(Note.objects.all())
        # The most recent should be first
        self.assertEqual(notes[0], note2)
        self.assertEqual(notes[1], note1)


class NoteSerializerTest(TestCase):
    """Tests for the Note serializer"""

    def test_serialize_note(self):
        """Test the serialization of a note"""
        from .serializers import NoteSerializer
        note = Note.objects.create(
            title="Test Note",
            content="Contenu de test"
        )
        serializer = NoteSerializer(note)
        data = dict(serializer.data)
        self.assertEqual(data['title'], "Test Note")
        self.assertEqual(data['content'], "Contenu de test")


class NoteViewSetTest(APITestCase):
    """Integration tests for the Note API endpoints."""

    def setUp(self):
        """Initial setup for each API test."""
        self.note1 = Note.objects.create(
            title="Note 1",
            content="Contenu 1"
        )
        self.note2 = Note.objects.create(
            title="Note 2",
            content="Contenu 2"
        )

    def test_list_notes(self):
        """Test the list of notes"""
        url = reverse('notes-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['title'], "Note 2")  # The most recent should be first

    def test_retrieve_note(self):
        """Test the retrieval of a note"""
        url = reverse('notes-detail', kwargs={'pk': self.note1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Note 1")
        self.assertEqual(response.data['content'], "Contenu 1")

    def test_create_note(self):
        """Test the creation of a note via API"""
        url = reverse('notes-list')
        data = {
            'title': 'Nouvelle Note',
            'content': 'Nouveau contenu'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Nouvelle Note')
        self.assertEqual(Note.objects.count(), 3)

    def test_update_note(self):
        """Test the update of a note"""
        url = reverse('notes-detail', kwargs={'pk': self.note1.pk})
        data = {
            'title': 'Note Modifiée',
            'content': 'Contenu modifié'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Note Modifiée')
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, 'Note Modifiée')

    def test_partial_update_note(self):
        """Test the partial update of a note"""
        url = reverse('notes-detail', kwargs={'pk': self.note1.pk})
        data = {'title': 'Titre Modifié'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Titre Modifié')
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, 'Titre Modifié')
        # The content should not be modified
        self.assertEqual(self.note1.content, 'Contenu 1')

    def test_delete_note(self):
        """Test the deletion of a note"""
        url = reverse('notes-detail', kwargs={'pk': self.note1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 1)
        self.assertFalse(Note.objects.filter(pk=self.note1.pk).exists())

    def test_create_note_validation(self):
        """Test the validation during the creation"""
        url = reverse('notes-list')
        # Missing title should trigger a validation error
        data = {'content': 'Contenu sans titre'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data['errors'])

    def test_delete_note_with_related_todos_blocked(self):
        """Deleting a note with todos should be blocked by validation."""
        todo = Todo.objects.create(title="Todo lié", note=self.note1)

        url = reverse('notes-detail', kwargs={'pk': self.note1.pk})
        response = self.client.delete(url)

        # Should return 400 because the note has todos
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('note_has_todos', response.data.get('code', ''))
        
        # Note should still exist
        self.assertTrue(Note.objects.filter(pk=self.note1.pk).exists())

class NoteValidationTest(TestCase):
    """Test cases for Note model validation rules."""

    def setUp(self):
        """Set up test data."""
        self.note = Note.objects.create(
            title="Test Note",
            content="Test content"
        )

    def test_note_creation_default_status(self):
        """Test that a new note has ACTIVE status by default."""
        self.assertEqual(self.note.status, NoteStatus.ACTIVE)

    def test_delete_note_without_todos(self):
        """Test that a note without todos can be deleted."""
        note_id = self.note.pk
        self.note.delete()
        self.assertFalse(Note.objects.filter(pk=note_id).exists())

    def test_delete_note_with_todos_raises_error(self):
        """Test that deleting a note with todos raises ValidationError."""
        # Create a todo associated with the note
        Todo.objects.create(
            title="Test Todo",
            note=self.note,
            status=TodoStatus.PENDING
        )
        
        # Attempt to delete should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.note.delete()
        
        self.assertIn("Cannot delete note", str(context.exception))

    def test_update_status_no_todos(self):
        """Test status update when note has no todos."""
        self.note.status = NoteStatus.IN_PROGRESS
        self.note.save()
        
        updated = self.note.update_status_from_todos()
        self.assertTrue(updated)
        self.assertEqual(self.note.status, NoteStatus.ACTIVE)

    def test_update_status_all_completed(self):
        """Test status update when all todos are completed."""
        Todo.objects.create(
            title="Todo 1",
            note=self.note,
            status=TodoStatus.COMPLETED
        )
        Todo.objects.create(
            title="Todo 2",
            note=self.note,
            status=TodoStatus.COMPLETED
        )
        
        self.note.update_status_from_todos()
        self.assertEqual(self.note.status, NoteStatus.COMPLETED)

    def test_update_status_with_in_progress(self):
        """Test status update when at least one todo is in progress."""
        Todo.objects.create(
            title="Todo 1",
            note=self.note,
            status=TodoStatus.IN_PROGRESS
        )
        Todo.objects.create(
            title="Todo 2",
            note=self.note,
            status=TodoStatus.PENDING
        )
        
        self.note.update_status_from_todos()
        self.assertEqual(self.note.status, NoteStatus.IN_PROGRESS)

    def test_update_status_with_pending(self):
        """Test status update when todos are pending."""
        Todo.objects.create(
            title="Todo 1",
            note=self.note,
            status=TodoStatus.PENDING
        )
        
        self.note.update_status_from_todos()
        self.assertEqual(self.note.status, NoteStatus.ACTIVE)

    def test_archived_status_not_auto_updated(self):
        """Test that archived notes don't get auto-updated."""
        self.note.status = NoteStatus.ARCHIVED
        self.note.save()
        
        Todo.objects.create(
            title="Todo 1",
            note=self.note,
            status=TodoStatus.COMPLETED
        )
        
        updated = self.note.update_status_from_todos()
        self.assertFalse(updated)
        self.assertEqual(self.note.status, NoteStatus.ARCHIVED)


class NoteAPIValidationTest(APITestCase):
    """Test cases for Note API endpoints with validation rules."""

    def setUp(self):
        """Set up test data."""
        self.note = Note.objects.create(
            title="API Test Note",
            content="Test content"
        )
        self.list_url = reverse('notes-list')
        self.detail_url = reverse('notes-detail', kwargs={'pk': self.note.pk})

    def test_delete_note_with_todos_api(self):
        """Test that API returns 400 when trying to delete note with todos."""
        # Create a todo
        Todo.objects.create(
            title="Test Todo",
            note=self.note,
            status=TodoStatus.PENDING
        )
        
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('note_has_todos', response.data.get('code', ''))

    def test_delete_note_without_todos_api(self):
        """Test that API allows deletion of note without todos."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_note_serializer_includes_status(self):
        """Test that serializer includes status field."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], NoteStatus.ACTIVE)

    def test_note_serializer_includes_todos_count(self):
        """Test that serializer includes todos_count field."""
        Todo.objects.create(
            title="Test Todo",
            note=self.note,
            status=TodoStatus.PENDING
        )
        
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('todos_count', response.data)
        self.assertEqual(response.data['todos_count'], 1)


class TodoSignalTest(TestCase):
    """Test cases for automatic note status update via signals."""

    def setUp(self):
        """Set up test data."""
        self.note = Note.objects.create(
            title="Signal Test Note",
            content="Test content"
        )

    def test_create_todo_updates_note_status(self):
        """Test that creating a todo updates the note status."""
        Todo.objects.create(
            title="New Todo",
            note=self.note,
            status=TodoStatus.PENDING
        )
        
        self.note.refresh_from_db()
        self.assertEqual(self.note.status, NoteStatus.ACTIVE)

    def test_update_todo_updates_note_status(self):
        """Test that updating a todo updates the note status."""
        todo = Todo.objects.create(
            title="Todo",
            note=self.note,
            status=TodoStatus.PENDING
        )
        
        # Update todo to completed
        todo.status = TodoStatus.COMPLETED
        todo.save()
        
        self.note.refresh_from_db()
        self.assertEqual(self.note.status, NoteStatus.COMPLETED)

    def test_delete_todo_updates_note_status(self):
        """Test that deleting a todo updates the note status."""
        todo = Todo.objects.create(
            title="Todo",
            note=self.note,
            status=TodoStatus.IN_PROGRESS
        )
        
        self.note.refresh_from_db()
        self.assertEqual(self.note.status, NoteStatus.IN_PROGRESS)
        
        # Delete todo
        todo.delete()
        
        self.note.refresh_from_db()
        self.assertEqual(self.note.status, NoteStatus.ACTIVE)

    def test_multiple_todos_status_priority(self):
        """Test status calculation with multiple todos."""
        # Create pending todo
        Todo.objects.create(
            title="Todo 1",
            note=self.note,
            status=TodoStatus.PENDING
        )
        
        self.note.refresh_from_db()
        self.assertEqual(self.note.status, NoteStatus.ACTIVE)
        
        # Add in-progress todo (should take priority)
        Todo.objects.create(
            title="Todo 2",
            note=self.note,
            status=TodoStatus.IN_PROGRESS
        )
        
        self.note.refresh_from_db()
        self.assertEqual(self.note.status, NoteStatus.IN_PROGRESS)

