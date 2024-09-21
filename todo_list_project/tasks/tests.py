from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.task = Task.objects.create(
            title='Tarea de Prueba',
            description='Esta es una tarea de prueba',
            user=self.user
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Tarea de Prueba')
        self.assertEqual(self.task.description, 'Esta es una tarea de prueba')
        self.assertEqual(self.task.user, self.user)
        self.assertFalse(self.task.completed)

    def test_task_str_representation(self):
        self.assertEqual(str(self.task), 'Tarea de Prueba')


class TaskViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.task = Task.objects.create(
            title='Tarea de Prueba',
            description='Esta es una tarea de prueba',
            user=self.user
        )

    def test_task_list_view(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tarea de Prueba')

    def test_task_create_view(self):
        response = self.client.post(reverse('task_create'), {
            'title': 'Nueva Tarea',
            'description': 'Esta es una nueva tarea'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Task.objects.filter(title='Nueva Tarea').exists())

    def test_task_update_view(self):
        response = self.client.post(reverse('task_update', args=[self.task.id]), {
            'title': 'Tarea Actualizada',
            'description': 'Esta tarea ha sido actualizada'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Tarea Actualizada')

    def test_task_delete_view(self):
        response = self.client.post(reverse('task_delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_task_toggle_complete_view(self):
        response = self.client.post(reverse('task_toggle_complete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after toggle
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)

    def test_task_search(self):
        Task.objects.create(title='Otra Tarea', description='Esta es otra tarea', user=self.user)
        response = self.client.get(reverse('task_list') + '?query=prueba')
        self.assertContains(response, 'Tarea de Prueba')
        self.assertNotContains(response, 'Otra Tarea')


class TaskIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_task_lifecycle(self):
        # Create a task
        response = self.client.post(reverse('task_create'), {
            'title': 'Tarea de Prueba de Integración',
            'description': 'Esta es una tarea de prueba de integración'
        })
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='Tarea de Prueba de Integración')

        # Update the task
        response = self.client.post(reverse('task_update', args=[task.id]), {
            'title': 'Tarea de Prueba de Integración Actualizada',
            'description': 'Esta tarea ha sido actualizada'
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Tarea de Prueba de Integración Actualizada')

        # Toggle task completion
        response = self.client.post(reverse('task_toggle_complete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertTrue(task.completed)

        # Delete the task
        response = self.client.post(reverse('task_delete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())
