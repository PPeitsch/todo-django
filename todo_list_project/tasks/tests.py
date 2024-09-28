from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task
from django.test.utils import override_settings


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
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)

    def test_task_str_representation(self):
        self.assertEqual(str(self.task), 'Tarea de Prueba')

    def test_task_ordering(self):
        task2 = Task.objects.create(title='Tarea 2', user=self.user)
        tasks = Task.objects.all()
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], self.task)


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
        self.assertTemplateUsed(response, 'tasks/tasks_list.html')

    def test_task_create_view(self):
        response = self.client.post(reverse('task_create'), {
            'title': 'Nueva Tarea',
            'description': 'Esta es una nueva tarea'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Task.objects.filter(title='Nueva Tarea').exists())
        new_task = Task.objects.get(title='Nueva Tarea')
        self.assertEqual(new_task.user, self.user)

    def test_task_create_view_invalid_data(self):
        response = self.client.post(reverse('task_create'), {
            'title': '',  # Invalid: empty title
            'description': 'This task has no title'
        })
        self.assertEqual(response.status_code, 200)  # Stays on the same page
        self.assertFalse(Task.objects.filter(description='This task has no title').exists())
        self.assertContains(response, 'Este campo es obligatorio.')

    def test_task_update_view(self):
        response = self.client.post(reverse('task_update', args=[self.task.id]), {
            'title': 'Tarea Actualizada',
            'description': 'Esta tarea ha sido actualizada'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Tarea Actualizada')
        self.assertEqual(self.task.description, 'Esta tarea ha sido actualizada')

    def test_task_delete_view(self):
        response = self.client.post(reverse('task_delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_task_toggle_complete_view(self):
        response = self.client.post(reverse('task_toggle_complete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after toggle
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)

        # Toggle back to incomplete
        response = self.client.post(reverse('task_toggle_complete', args=[self.task.id]))
        self.task.refresh_from_db()
        self.assertFalse(self.task.completed)

    def test_task_search(self):
        Task.objects.create(title='Otra Tarea', description='Esta es otra tarea', user=self.user)
        response = self.client.get(reverse('task_list') + '?query=prueba')
        self.assertContains(response, 'Tarea de Prueba')
        self.assertNotContains(response, 'Otra Tarea')

    def test_task_list_ordering(self):
        Task.objects.all().delete()  # Limpiar todas las tareas existentes
        Task.objects.create(title='Tarea A', user=self.user)
        Task.objects.create(title='Tarea B', user=self.user)
        response = self.client.get(reverse('task_list'))
        tasks = list(response.context['tasks'])
        self.assertEqual(tasks[0].title, 'Tarea A')
        self.assertEqual(tasks[1].title, 'Tarea B')

    def test_task_list_chronological_order(self):
        Task.objects.all().delete()  # Limpiar todas las tareas existentes
        task1 = Task.objects.create(title='Tarea 1', user=self.user)
        task2 = Task.objects.create(title='Tarea 2', user=self.user)
        task3 = Task.objects.create(title='Tarea 3', user=self.user)

        response = self.client.get(reverse('task_list'))
        tasks = list(response.context['tasks'])

        self.assertEqual(tasks[0].title, 'Tarea 1')
        self.assertEqual(tasks[1].title, 'Tarea 2')
        self.assertEqual(tasks[2].title, 'Tarea 3')


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
        self.assertContains(response,
                            'Marcar como Incompleta')  # Verificar que el botón para marcar como incompleta está presente

        # Delete the task
        response = self.client.post(reverse('task_delete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

        # Verify task no longer in list view
        response = self.client.get(reverse('task_list'))
        self.assertNotContains(response, 'Tarea de Prueba de Integración Actualizada')


class TaskAccessControlTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='67890')
        self.task = Task.objects.create(title='User1 Task', user=self.user1)

    def test_user_can_only_see_own_tasks(self):
        self.client.login(username='user2', password='67890')
        response = self.client.get(reverse('task_list'))
        self.assertNotContains(response, 'User1 Task')

    def test_user_cannot_update_others_task(self):
        self.client.login(username='user2', password='67890')
        response = self.client.post(reverse('task_update', args=[self.task.id]), {
            'title': 'Updated by User2',
            'description': 'This should not work'
        })
        self.assertEqual(response.status_code, 404)
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.title, 'Updated by User2')

    def test_user_cannot_delete_others_task(self):
        self.client.login(username='user2', password='67890')
        response = self.client.post(reverse('task_delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())


@override_settings(LANGUAGE_CODE='en-us')
class TaskInternationalizationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_task_list_uses_translations(self):
        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'My Tasks')  # Assuming 'My Tasks' is a translated string

    def test_task_create_form_uses_translations(self):
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Task')  # Assuming 'Create Task' is a translated string
