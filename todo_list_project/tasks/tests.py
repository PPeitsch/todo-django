import time
from functools import wraps
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Task
from django.test import override_settings


def ensure_unique_timestamps(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        original_time = timezone.now
        try:
            timezone.now = lambda: original_time() + timezone.timedelta(
                microseconds=time.monotonic_ns() // 1000 % 1000000)
            return func(*args, **kwargs)
        finally:
            timezone.now = original_time

    return wrapper


class TaskModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')

    def create_task(self, title, description=''):
        task = Task.objects.create(title=title, description=description, user=self.user)
        time.sleep(0.001)
        return task

    @ensure_unique_timestamps
    def test_task_creation(self):
        task = self.create_task('Tarea de Prueba', 'Esta es una tarea de prueba')
        self.assertEqual(task.title, 'Tarea de Prueba')
        self.assertEqual(task.description, 'Esta es una tarea de prueba')
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.completed)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)

    @ensure_unique_timestamps
    def test_task_str_representation(self):
        task = self.create_task('Tarea de Prueba')
        self.assertEqual(str(task), 'Tarea de Prueba')

    @ensure_unique_timestamps
    def test_task_ordering(self):
        task1 = self.create_task('Tarea 1')
        task2 = self.create_task('Tarea 2')
        tasks = Task.objects.all()
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], task1)


class TaskViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def create_task(self, title, description=''):
        task = Task.objects.create(title=title, description=description, user=self.user)
        time.sleep(0.001)
        return task

    @ensure_unique_timestamps
    def test_task_list_view(self):
        task1 = self.create_task('Tarea de Prueba 1')
        task2 = self.create_task('Tarea de Prueba 2')
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tarea de Prueba 1')
        self.assertContains(response, 'Tarea de Prueba 2')
        self.assertTemplateUsed(response, 'tasks/tasks_list.html')
        tasks = list(response.context['tasks'])
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], task1)

    @ensure_unique_timestamps
    def test_task_create_view(self):
        response = self.client.post(reverse('task_create'), {
            'title': 'Nueva Tarea',
            'description': 'Esta es una nueva tarea'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='Nueva Tarea').exists())
        new_task = Task.objects.get(title='Nueva Tarea')
        self.assertEqual(new_task.user, self.user)

    @ensure_unique_timestamps
    def test_task_create_view_invalid_data(self):
        response = self.client.post(reverse('task_create'), {
            'title': '',
            'description': 'This task has no title'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(description='This task has no title').exists())
        self.assertContains(response, 'Este campo es obligatorio.')

    @ensure_unique_timestamps
    def test_task_update_view(self):
        task = self.create_task('Tarea Original')
        response = self.client.post(reverse('task_update', args=[task.id]), {
            'title': 'Tarea Actualizada',
            'description': 'Esta tarea ha sido actualizada'
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Tarea Actualizada')
        self.assertEqual(task.description, 'Esta tarea ha sido actualizada')

    @ensure_unique_timestamps
    def test_task_delete_view(self):
        task = self.create_task('Tarea a Eliminar')
        response = self.client.post(reverse('task_delete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    @ensure_unique_timestamps
    def test_task_toggle_complete_view(self):
        task = self.create_task('Tarea Toggle')
        response = self.client.post(reverse('task_toggle_complete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertTrue(task.completed)

        response = self.client.post(reverse('task_toggle_complete', args=[task.id]))
        task.refresh_from_db()
        self.assertFalse(task.completed)

    @ensure_unique_timestamps
    def test_task_search(self):
        self.create_task('Tarea de Prueba')
        self.create_task('Otra Tarea')
        response = self.client.get(reverse('task_list') + '?query=prueba')
        self.assertContains(response, 'Tarea de Prueba')
        self.assertNotContains(response, 'Otra Tarea')

    @ensure_unique_timestamps
    def test_task_list_ordering(self):
        Task.objects.all().delete()
        self.create_task('Tarea A')
        self.create_task('Tarea B')
        response = self.client.get(reverse('task_list'))
        tasks = list(response.context['tasks'])
        self.assertEqual(tasks[0].title, 'Tarea B')
        self.assertEqual(tasks[1].title, 'Tarea A')

    @ensure_unique_timestamps
    def test_task_list_chronological_order(self):
        Task.objects.all().delete()
        self.create_task('Tarea 1')
        self.create_task('Tarea 2')
        self.create_task('Tarea 3')

        response = self.client.get(reverse('task_list'))
        tasks = list(response.context['tasks'])

        self.assertEqual(tasks[0].title, 'Tarea 3')
        self.assertEqual(tasks[1].title, 'Tarea 2')
        self.assertEqual(tasks[2].title, 'Tarea 1')


class TaskIntegrationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    @ensure_unique_timestamps
    def test_task_lifecycle(self):
        # Create a task
        response = self.client.post(reverse('task_create'), {
            'title': 'Tarea de Prueba de Integración',
            'description': 'Esta es una tarea de prueba de integración'
        })
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='Tarea de Prueba de Integración')

        # Verify task in list view
        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'Tarea de Prueba de Integración')

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

        # Verify completed task in list view
        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'Tarea de Prueba de Integración Actualizada')
        self.assertContains(response, 'Marcar como Incompleta')

        # Delete the task
        response = self.client.post(reverse('task_delete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

        # Verify task no longer in list view
        response = self.client.get(reverse('task_list'))
        self.assertNotContains(response, 'Tarea de Prueba de Integración Actualizada')


class TaskAccessControlTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1', password='12345')
        cls.user2 = User.objects.create_user(username='user2', password='67890')

    def setUp(self):
        self.client = Client()
        self.task = Task.objects.create(title='User1 Task', user=self.user1)

    @ensure_unique_timestamps
    def test_user_can_only_see_own_tasks(self):
        self.client.login(username='user2', password='67890')
        response = self.client.get(reverse('task_list'))
        self.assertNotContains(response, 'User1 Task')

    @ensure_unique_timestamps
    def test_user_cannot_update_others_task(self):
        self.client.login(username='user2', password='67890')
        response = self.client.post(reverse('task_update', args=[self.task.id]), {
            'title': 'Updated by User2',
            'description': 'This should not work'
        })
        self.assertEqual(response.status_code, 404)
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.title, 'Updated by User2')

    @ensure_unique_timestamps
    def test_user_cannot_delete_others_task(self):
        self.client.login(username='user2', password='67890')
        response = self.client.post(reverse('task_delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())


class TaskInternationalizationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    @override_settings(LANGUAGE_CODE='en')
    @ensure_unique_timestamps
    def test_task_list_uses_translations(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Tasks')

    @override_settings(LANGUAGE_CODE='en')
    @ensure_unique_timestamps
    def test_task_create_form_uses_translations(self):
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Task')
