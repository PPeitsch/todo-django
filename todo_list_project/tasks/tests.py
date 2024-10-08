import time
from functools import wraps
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Task
from django.test import override_settings
from django.utils.translation import gettext as _, activate


def ensure_unique_timestamps(func):
    """
    Decorator to ensure unique timestamps for each task creation.

    This decorator modifies the timezone.now() function to return a unique
    timestamp for each call, ensuring that tasks created in rapid succession
    have distinct creation times.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The wrapped function with unique timestamp functionality.
    """

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
    """
    Test case for the Task model.

    This class contains tests to verify the functionality of the Task model,
    including task creation, string representation, and ordering.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.

        This method is called once at the beginning of the test case to set up
        non-modified data for all test methods.
        """
        cls.user = User.objects.create_user(username='testuser', password='12345')

    def create_task(self, title, description=''):
        """
        Helper method to create a task.

        Args:
            title (str): The title of the task.
            description (str, optional): The description of the task. Defaults to ''.

        Returns:
            Task: The created task object.
        """
        task = Task.objects.create(title=title, description=description, user=self.user)
        time.sleep(0.001)
        return task

    @ensure_unique_timestamps
    def test_task_creation(self):
        """
        Test task creation functionality.

        This test verifies that a task can be created with the correct attributes.
        """
        task = self.create_task('Test Task', 'This is a test task')
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.description, 'This is a test task')
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.completed)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)

    @ensure_unique_timestamps
    def test_task_str_representation(self):
        """
        Test the string representation of a task.

        This test verifies that the string representation of a task is its title.
        """
        task = self.create_task('Test Task')
        self.assertEqual(str(task), 'Test Task')

    @ensure_unique_timestamps
    def test_task_ordering(self):
        """
        Test the default ordering of tasks.

        This test verifies that tasks are ordered by their creation time in descending order.
        """
        task1 = self.create_task('Task 1')
        task2 = self.create_task('Task 2')
        tasks = Task.objects.all()
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], task1)


class TaskViewsTest(TestCase):
    """
    Test case for the Task views.

    This class contains tests to verify the functionality of the Task views,
    including list view, creation, update, deletion, and search.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.

        This method is called once at the beginning of the test case to set up
        non-modified data for all test methods.
        """
        cls.user = User.objects.create_user(username='testuser', password='12345')

    def setUp(self):
        """
        Set up data for each test.

        This method is called before each test method to set up any objects that
        may be modified by the test.
        """
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    @ensure_unique_timestamps
    def test_task_list_view(self):
        """
        Test the task list view.

        This test verifies that the task list view displays all tasks for the user.
        """
        task1 = self.create_task('Test Task 1')
        task2 = self.create_task('Test Task 2')
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task 1')
        self.assertContains(response, 'Test Task 2')
        self.assertTemplateUsed(response, 'tasks/tasks_list.html')
        tasks = list(response.context['tasks'])
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], task1)

    @ensure_unique_timestamps
    def test_task_create_view(self):
        """
        Test the task creation view.

        This test verifies that a new task can be created through the create view.
        """
        response = self.client.post(reverse('task_create'), {
            'title': 'New Task',
            'description': 'This is a new task'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())
        new_task = Task.objects.get(title='New Task')
        self.assertEqual(new_task.user, self.user)

    def test_task_create_view_invalid_data_multilingual(self):
        """
        Test the task creation view with invalid data in multiple languages.

        This test verifies that the create view handles invalid data correctly
        and displays appropriate error messages in both English and Spanish.
        """
        for lang_code in ['en', 'es']:
            for lang_code in ['en', 'es']:
                with self.subTest(lang=lang_code), override_settings(LANGUAGE_CODE=lang_code):
                     activate(lang_code)
                     response = self.client.post(reverse('task_create'), {
                         'title': '',
                    activate(lang_code)
                    response = self.client.post(reverse('task_create'), {
                        'title': '',
                        'description': 'This task has no title'
                    })
                    self.assertEqual(response.status_code, 200)
                    self.assertFalse(Task.objects.filter(description='This task has no title').exists())
                    expected_error = _('This field is required.')
                    self.assertContains(response, expected_error)

    @ensure_unique_timestamps
    def test_task_update_view(self):
        """
        Test the task update view.

        This test verifies that a task can be updated through the update view.
        """
        task = self.create_task('Original Task')
        response = self.client.post(reverse('task_update', args=[task.id]), {
            'title': 'Updated Task',
            'description': 'This task has been updated'
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Task')
        self.assertEqual(task.description, 'This task has been updated')

    @ensure_unique_timestamps
    def test_task_delete_view(self):
        """
        Test the task delete view.

        This test verifies that a task can be deleted through the delete view.
        """
        task = self.create_task('Task to Delete')
        response = self.client.post(reverse('task_delete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    @ensure_unique_timestamps
    def test_task_toggle_complete_view(self):
        """
        Test the task toggle complete view.

        This test verifies that a task's completed status can be toggled.
        """
        task = self.create_task('Toggle Task')

        # Toggle to complete
        response = self.client.post(reverse('task_toggle_complete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertTrue(task.completed)

        # Toggle back to incomplete
        self.client.post(reverse('task_toggle_complete', args=[task.id]))
        task.refresh_from_db()
        self.assertFalse(task.completed)

    @ensure_unique_timestamps
    def test_task_search(self):
        """
        Test the task search functionality.

        This test verifies that tasks can be searched by title.
        """
        self.create_task('Test Task')
        self.create_task('Another Task')
        response = self.client.get(reverse('task_list') + '?query=test')
        self.assertContains(response, 'Test Task')
        self.assertNotContains(response, 'Another Task')

    @ensure_unique_timestamps
    def test_task_list_ordering(self):
        """
        Test the ordering of tasks in the list view.

        This test verifies that tasks are displayed in the correct order in the list view.
        """
        Task.objects.all().delete()
        self.create_task('Task A')
        self.create_task('Task B')
        response = self.client.get(reverse('task_list'))
        tasks = list(response.context['tasks'])
        self.assertEqual(tasks[0].title, 'Task B')
        self.assertEqual(tasks[1].title, 'Task A')

    @ensure_unique_timestamps
    def test_task_list_chronological_order(self):
        """
        Test the chronological ordering of tasks in the list view.

        This test verifies that tasks are displayed in chronological order in the list view.
        """
        Task.objects.all().delete()
        self.create_task('Task 1')
        self.create_task('Task 2')
        self.create_task('Task 3')

        response = self.client.get(reverse('task_list'))
        tasks = list(response.context['tasks'])

        self.assertEqual(tasks[0].title, 'Task 3')
        self.assertEqual(tasks[1].title, 'Task 2')
        self.assertEqual(tasks[2].title, 'Task 1')

    def create_task(self, title, description=''):
        """
        Helper method to create a task.

        Args:
            title (str): The title of the task.
            description (str, optional): The description of the task. Defaults to ''.

        Returns:
            Task: The created task object.
        """
        task = Task.objects.create(title=title, description=description, user=self.user)
        time.sleep(0.001)
        return task


class TaskIntegrationTest(TestCase):
    """
    Integration test case for the Task functionality.

    This class contains tests to verify the integration of various Task operations,
    simulating a complete task lifecycle.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.

        This method is called once at the beginning of the test case to set up
        non-modified data for all test methods.
        """
        cls.user = User.objects.create_user(username='testuser', password='12345')

    def setUp(self):
        """
        Set up data for each test.

        This method is called before each test method to set up any objects that
        may be modified by the test.
        """
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def test_task_lifecycle_multilingual(self):
        """
        Test the complete lifecycle of a task in multiple languages.

        This test simulates creating, updating, completing, and deleting a task,
        verifying each step of the process in both English and Spanish.
        """
        for lang_code in ['en', 'es']:
        for lang_code in ['en', 'es']:
            with self.subTest(lang=lang_code), override_settings(LANGUAGE_CODE=lang_code):
                activate(lang_code)
                self._run_task_lifecycle_test()
                    activate(lang_code)
                    self._run_task_lifecycle_test()

    @ensure_unique_timestamps
    def _run_task_lifecycle_test(self):
        """
        Run the task lifecycle test for a single language.

        This method contains the core logic for testing the task lifecycle,
        including creation, update, completion, and deletion.
        """
        response = self.client.post(reverse('task_create'), {
            'title': 'Integration Test Task',
            'description': 'This is an integration test task'
        })
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='Integration Test Task')

        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'Integration Test Task')

        response = self.client.post(reverse('task_update', args=[task.id]), {
            'title': 'Updated Integration Test Task',
            'description': 'This task has been updated'
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Integration Test Task')

        response = self.client.post(reverse('task_toggle_complete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertTrue(task.completed)

        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'Updated Integration Test Task')
        self.assertContains(response, _('Mark as Incomplete'))

        response = self.client.post(reverse('task_delete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

        response = self.client.get(reverse('task_list'))
        self.assertNotContains(response, 'Updated Integration Test Task')

        Task.objects.all().delete()


class TaskAccessControlTest(TestCase):
    """
    Test case for Task access control.

    This class contains tests to verify that users can only access and modify
    their own tasks, and cannot access or modify tasks belonging to other users.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.

        This method is called once at the beginning of the test case to set up
        non-modified data for all test methods.
        """
        cls.user1 = User.objects.create_user(username='user1', password='12345')
        cls.user2 = User.objects.create_user(username='user2', password='67890')

    def setUp(self):
        """
        Set up data for each test.

        This method is called before each test method to set up any objects that
        may be modified by the test.
        """
        self.client = Client()
        self.task = Task.objects.create(title='User1 Task', user=self.user1)

    @ensure_unique_timestamps
    def test_user_can_only_see_own_tasks(self):
        """
        Test that a user can only see their own tasks.

        This test verifies that a user cannot see tasks belonging to other users.
        """
        self.client.login(username='user2', password='67890')
        response = self.client.get(reverse('task_list'))
        self.assertNotContains(response, 'User1 Task')

    @ensure_unique_timestamps
    def test_user_cannot_update_others_task(self):
        """
        Test that a user cannot update tasks belonging to other users.

        This test verifies that a user cannot modify tasks that don't belong to them.
        """
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
        """
        Test that a user cannot delete tasks belonging to other users.

        This test verifies that a user cannot delete tasks that don't belong to them.
        """
        self.client.login(username='user2', password='67890')
        response = self.client.post(reverse('task_delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())


class TaskInternationalizationTest(TestCase):
    """
    Test case for Task internationalization.

    This class contains tests to verify that the task-related pages and
    functionality work correctly with different language settings.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.

        This method is called once at the beginning of the test case to set up
        non-modified data for all test methods.
        """
        cls.user = User.objects.create_user(username='testuser', password='12345')

    def setUp(self):
        """
        Set up data for each test.

        This method is called before each test method to set up any objects that
        may be modified by the test.
        """
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    @override_settings(LANGUAGE_CODE='en')
    @ensure_unique_timestamps
    def test_task_list_uses_english_translations(self):
        """
        Test that the task list uses English translations when the language is set to English.

        This test verifies that the task list page contains the correct English text.
        """
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Tasks')

    @override_settings(LANGUAGE_CODE='es')
    @ensure_unique_timestamps
    def test_task_list_uses_spanish_translations(self):
        """
        Test that the task list uses Spanish translations when the language is set to Spanish.

        This test verifies that the task list page contains the correct Spanish text.
        """
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mis Tareas')

    @override_settings(LANGUAGE_CODE='en')
    @ensure_unique_timestamps
    def test_task_create_form_uses_english_translations(self):
        """
        Test that the task creation form uses English translations when the language is set to English.

        This test verifies that the task creation page contains the correct English text.
        """
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Task')

    @override_settings(LANGUAGE_CODE='es')
    @ensure_unique_timestamps
    def test_task_create_form_uses_spanish_translations(self):
        """
        Test that the task creation form uses Spanish translations when the language is set to Spanish.

        This test verifies that the task creation page contains the correct Spanish text.
        """
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crear Tarea')

    def test_translation_consistency(self):
        """
        Test the consistency of translations across different language settings.

        This test verifies that certain key phrases are correctly translated in both English and Spanish.
        """
        with override_settings(LANGUAGE_CODE='en'):
            self.assertEqual(_('My Tasks'), 'My Tasks')
            self.assertEqual(_('Create Task'), 'Create Task')

        with override_settings(LANGUAGE_CODE='es'):
            self.assertEqual(_('My Tasks'), 'Mis Tareas')
            self.assertEqual(_('Create Task'), 'Crear Tarea')