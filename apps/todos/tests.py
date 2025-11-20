from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from .models import Todo, TodoStatus
from apps.notes.models import Note


class TodoModelTest(TestCase):
    """Unit tests for the Todo model."""

    def test_create_todo(self):
        """Should create a Todo instance with all fields."""
        todo = Todo.objects.create(
            title="Test Todo",
            description="Description de test",
            status=TodoStatus.PENDING
        )
        self.assertEqual(todo.title, "Test Todo")
        self.assertEqual(todo.description, "Description de test")
        self.assertEqual(todo.status, TodoStatus.PENDING)
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)

    def test_todo_default_status(self):
        """Should default status to pending when unspecified."""
        todo = Todo.objects.create(title="Todo sans statut")
        self.assertEqual(todo.status, TodoStatus.PENDING)

    def test_todo_str(self):
        """Should render a readable string representation."""
        todo = Todo.objects.create(
            title="Ma Todo",
            status=TodoStatus.IN_PROGRESS
        )
        self.assertIn("Ma Todo", str(todo))
        self.assertIn("In Progress", str(todo))

    def test_todo_with_note(self):
        """Should link a todo to a note."""
        note = Note.objects.create(title="Note Test", content="Content")
        todo = Todo.objects.create(
            title="Todo avec note",
            note=note
        )
        self.assertEqual(todo.note, note)
        self.assertIn(todo, note.todos.all())

    def test_todo_without_note(self):
        """Should allow todos without a related note."""
        todo = Todo.objects.create(title="Todo sans note")
        self.assertIsNone(todo.note)

    def test_todo_ordering(self):
        """Should order todos with newest first."""
        todo1 = Todo.objects.create(title="Todo 1")
        todo2 = Todo.objects.create(title="Todo 2")
        todos = list(Todo.objects.all())
        # Newest entry must be first
        self.assertEqual(todos[0], todo2)
        self.assertEqual(todos[1], todo1)

    def test_todo_status_choices(self):
        """Should respect the status enum choices."""
        todo = Todo.objects.create(
            title="Todo",
            status=TodoStatus.COMPLETED
        )
        self.assertEqual(todo.status, TodoStatus.COMPLETED)
        self.assertEqual(todo.get_status_display(), "Completed")


class TodoSerializerTest(TestCase):
    """Tests for the Todo serializer."""

    def test_serialize_todo(self):
        """Should serialize a todo instance to JSON-friendly data."""
        from .serializers import TodoSerializer
        note = Note.objects.create(title="Note", content="Content")
        todo = Todo.objects.create(
            title="Test Todo",
            description="Description",
            status=TodoStatus.IN_PROGRESS,
            note=note
        )
        serializer = TodoSerializer(todo)
        data: dict = dict(serializer.data)
        
        self.assertEqual(data['title'], "Test Todo")
        self.assertEqual(data['description'], "Description")
        self.assertEqual(data['status'], TodoStatus.IN_PROGRESS)
        self.assertEqual(data['note'], note.pk)
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_deserialize_todo(self):
        """Should deserialize payloads and create a todo."""
        from .serializers import TodoSerializer
        note = Note.objects.create(title="Note", content="Content")
        data = {
            'title': 'Nouveau Todo',
            'description': 'Description',
            'status': TodoStatus.PENDING,
            'note': note.pk
        }
        serializer = TodoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        todo = serializer.save()
        self.assertEqual(todo.title, 'Nouveau Todo')
        self.assertEqual(todo.note, note)


class TodoViewSetTest(APITestCase):
    """Integration tests for the Todo API endpoints."""

    def setUp(self):
        """Initial setup for each test."""
        self.note = Note.objects.create(
            title="Note Test",
            content="Content"
        )
        self.todo1 = Todo.objects.create(
            title="Todo 1",
            description="Description 1",
            status=TodoStatus.PENDING,
            note=self.note
        )
        self.todo2 = Todo.objects.create(
            title="Todo 2",
            description="Description 2",
            status=TodoStatus.IN_PROGRESS
        )

    def test_list_todos(self):
        """Should list todos with pagination metadata."""
        url = reverse('todos-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['title'], "Todo 2")  # Plus récent en premier

    def test_retrieve_todo(self):
        """Should fetch a single todo."""
        url = reverse('todos-detail', kwargs={'pk': self.todo1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Todo 1")
        self.assertEqual(response.data['status'], TodoStatus.PENDING)
        self.assertEqual(response.data['note'], self.note.pk)

    def test_create_todo(self):
        """Should allow creating a todo via API."""
        url = reverse('todos-list')
        data = {
            'title': 'Nouveau Todo',
            'description': 'Nouvelle description',
            'status': TodoStatus.PENDING,
            'note': self.note.pk
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Nouveau Todo')
        self.assertEqual(Todo.objects.count(), 3)

    def test_create_todo_without_note(self):
        """Should accept todos without an associated note."""
        url = reverse('todos-list')
        data = {
            'title': 'Todo sans note',
            'status': TodoStatus.PENDING
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['note'])
        self.assertEqual(Todo.objects.count(), 3)

    def test_update_todo(self):
        """Should fully update a todo."""
        url = reverse('todos-detail', kwargs={'pk': self.todo1.pk})
        data = {
            'title': 'Todo Modifié',
            'description': 'Description modifiée',
            'status': TodoStatus.COMPLETED,
            'note': self.note.pk
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Todo Modifié')
        self.assertEqual(response.data['status'], TodoStatus.COMPLETED)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.status, TodoStatus.COMPLETED)

    def test_partial_update_todo_status(self):
        """Should partially update only the status field."""
        url = reverse('todos-detail', kwargs={'pk': self.todo1.pk})
        data = {'status': TodoStatus.COMPLETED}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], TodoStatus.COMPLETED)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.status, TodoStatus.COMPLETED)
        # Title must remain untouched
        self.assertEqual(self.todo1.title, 'Todo 1')

    def test_delete_todo(self):
        """Should delete a todo."""
        url = reverse('todos-detail', kwargs={'pk': self.todo1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Todo.objects.count(), 1)
        self.assertFalse(Todo.objects.filter(pk=self.todo1.pk).exists())

    def test_todo_with_note_relationship(self):
        """Should persist the note relationship through the API."""
        url = reverse('todos-list')
        data = {
            'title': 'Todo avec note',
            'note': self.note.pk
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        todo = Todo.objects.get(pk=response.data['id'])
        self.assertEqual(todo.note, self.note)
        self.assertIn(todo, self.note.todos.all())

    def test_create_todo_validation(self):
        """Should validate required fields."""
        url = reverse('todos-list')
        # Missing title should trigger validation errors
        data = {'status': TodoStatus.PENDING}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_todo_status_choices_validation(self):
        """Should reject invalid status values."""
        url = reverse('todos-list')
        data = {
            'title': 'Todo',
            'status': 'invalid_status'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_create_todo_with_unknown_note(self):
        """Should fail when the note foreign key does not exist."""
        url = reverse('todos-list')
        data = {
            'title': 'Todo orphelin',
            'note': 99999,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('note', response.data)

    def test_reassign_todo_to_another_note(self):
        """Should allow reassigning a todo to another note."""
        new_note = Note.objects.create(title="Autre note", content="Texte")
        url = reverse('todos-detail', kwargs={'pk': self.todo1.pk})
        data = {
            'note': new_note.pk,
            'title': self.todo1.title,
            'description': self.todo1.description,
            'status': self.todo1.status,
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.note, new_note)
