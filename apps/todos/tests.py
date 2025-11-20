from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from .models import Todo, TodoStatus
from apps.notes.models import Note


class TodoModelTest(TestCase):
    """Tests pour le modèle Todo"""

    def test_create_todo(self):
        """Test de création d'un todo"""
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
        """Test du statut par défaut"""
        todo = Todo.objects.create(title="Todo sans statut")
        self.assertEqual(todo.status, TodoStatus.PENDING)

    def test_todo_str(self):
        """Test de la méthode __str__"""
        todo = Todo.objects.create(
            title="Ma Todo",
            status=TodoStatus.IN_PROGRESS
        )
        self.assertIn("Ma Todo", str(todo))
        self.assertIn("In Progress", str(todo))

    def test_todo_with_note(self):
        """Test de la relation avec une note"""
        note = Note.objects.create(title="Note Test", content="Content")
        todo = Todo.objects.create(
            title="Todo avec note",
            note=note
        )
        self.assertEqual(todo.note, note)
        self.assertIn(todo, note.todos.all())

    def test_todo_without_note(self):
        """Test d'un todo sans note (relation optionnelle)"""
        todo = Todo.objects.create(title="Todo sans note")
        self.assertIsNone(todo.note)

    def test_todo_ordering(self):
        """Test de l'ordonnancement par date de création"""
        todo1 = Todo.objects.create(title="Todo 1")
        todo2 = Todo.objects.create(title="Todo 2")
        todos = list(Todo.objects.all())
        # La plus récente doit être en premier
        self.assertEqual(todos[0], todo2)
        self.assertEqual(todos[1], todo1)

    def test_todo_status_choices(self):
        """Test des choix de statut"""
        todo = Todo.objects.create(
            title="Todo",
            status=TodoStatus.COMPLETED
        )
        self.assertEqual(todo.status, TodoStatus.COMPLETED)
        self.assertEqual(todo.get_status_display(), "Completed")


class TodoSerializerTest(TestCase):
    """Tests pour le serializer Todo"""

    def test_serialize_todo(self):
        """Test de sérialisation d'un todo"""
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
        """Test de désérialisation pour créer un todo"""
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
    """Tests pour les endpoints API de Todo"""

    def setUp(self):
        """Configuration initiale pour les tests"""
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
        """Test de la liste des todos"""
        url = reverse('todos-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['title'], "Todo 2")  # Plus récent en premier

    def test_retrieve_todo(self):
        """Test de récupération d'un todo"""
        url = reverse('todos-detail', kwargs={'pk': self.todo1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Todo 1")
        self.assertEqual(response.data['status'], TodoStatus.PENDING)
        self.assertEqual(response.data['note'], self.note.pk)

    def test_create_todo(self):
        """Test de création d'un todo via API"""
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
        """Test de création d'un todo sans note"""
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
        """Test de mise à jour d'un todo"""
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
        """Test de mise à jour partielle du statut"""
        url = reverse('todos-detail', kwargs={'pk': self.todo1.pk})
        data = {'status': TodoStatus.COMPLETED}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], TodoStatus.COMPLETED)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.status, TodoStatus.COMPLETED)
        # Le titre ne doit pas être modifié
        self.assertEqual(self.todo1.title, 'Todo 1')

    def test_delete_todo(self):
        """Test de suppression d'un todo"""
        url = reverse('todos-detail', kwargs={'pk': self.todo1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Todo.objects.count(), 1)
        self.assertFalse(Todo.objects.filter(pk=self.todo1.pk).exists())

    def test_todo_with_note_relationship(self):
        """Test de la relation todo-note via API"""
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
        """Test de validation lors de la création"""
        url = reverse('todos-list')
        # Test sans titre (requis)
        data = {'status': TodoStatus.PENDING}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_todo_status_choices_validation(self):
        """Test de validation des choix de statut"""
        url = reverse('todos-list')
        data = {
            'title': 'Todo',
            'status': 'invalid_status'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
