from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from .models import Note
from apps.todos.models import Todo


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

    def test_note_with_todos(self):
        """Test the relation with the todos"""
        note = Note.objects.create(title="Note avec todos", content="Content")
        todo1 = Todo.objects.create(title="Todo 1", note=note)
        todo2 = Todo.objects.create(title="Todo 2", note=note)
        
        # Verify the inverse relation
        self.assertEqual(note.todos.count(), 2)
        self.assertIn(todo1, note.todos.all())
        self.assertIn(todo2, note.todos.all())


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

    def test_delete_note_sets_related_todos_to_null(self):
        """Deleting a note should not delete todos but reset their FK."""
        todo = Todo.objects.create(title="Todo lié", note=self.note1)

        url = reverse('notes-detail', kwargs={'pk': self.note1.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        todo.refresh_from_db()
        self.assertIsNone(todo.note)
