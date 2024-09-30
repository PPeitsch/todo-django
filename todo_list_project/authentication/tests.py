from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.conf import settings
from django.utils.translation import activate


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    def test_urls_resolve(self):
        # Spanish test
        with self.settings(LANGUAGE_CODE='es'):
            activate('es')
            self.assertEqual(resolve('/es/auth/login/').view_name, 'login')
            self.assertEqual(resolve('/es/auth/signup/').view_name, 'signup')
            self.assertEqual(resolve('/es/auth/logout/').view_name, 'logout')

        # English test
        with self.settings(LANGUAGE_CODE='en'):
            activate('en')
            self.assertEqual(resolve('/en/auth/login/').view_name, 'login')
            self.assertEqual(resolve('/en/auth/signup/').view_name, 'signup')
            self.assertEqual(resolve('/en/auth/logout/').view_name, 'logout')

    @override_settings(LANGUAGE_CODE='en-us')
    def test_signup_view_en(self):
        activate('en')
        self._test_signup_view()

    @override_settings(LANGUAGE_CODE='es')
    def test_signup_view_es(self):
        activate('es')
        self._test_signup_view()

    def _test_signup_view(self):
        self.client.logout()

        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/signup.html')

        # Test successful registration
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # Test failed registration (username already exists)
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'anotherpassword123',
            'password2': 'anotherpassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)
        self.assertRedirects(response, reverse('home'))

    def test_login_view(self):
        self.client.logout()
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')

        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_authenticated_user_redirect(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('home'))
        response = self.client.get(reverse('signup'))
        self.assertRedirects(response, reverse('home'))

    def test_unauthenticated_user_access(self):
        self.client.logout()
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_language_in_url(self):
        for lang_code in ['en', 'es']:
            activate(lang_code)
            response = self.client.get(reverse('login'))
            self.assertEqual(response.status_code, 200)
            self.assertIn(f'/{lang_code}/', response.request['PATH_INFO'])

            response = self.client.get(reverse('signup'))
            self.assertEqual(response.status_code, 200)
            self.assertIn(f'/{lang_code}/', response.request['PATH_INFO'])

    @override_settings(LANGUAGE_CODE='en-us')
    def test_signup_password_mismatch_en(self):
        activate('en')
        self._test_signup_password_mismatch()

    @override_settings(LANGUAGE_CODE='es')
    def test_signup_password_mismatch_es(self):
        activate('es')
        self._test_signup_password_mismatch()

    def _test_signup_password_mismatch(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'password123',
            'password2': 'password321',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context and response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_settings_configuration(self):
        self.assertIn('django.contrib.auth', settings.INSTALLED_APPS)
        self.assertIn('authentication.apps.AuthenticationConfig', settings.INSTALLED_APPS)
        self.assertEqual(settings.ROOT_URLCONF, 'todo_list_project.urls')
        self.assertIn('django.middleware.security.SecurityMiddleware', settings.MIDDLEWARE)
        self.assertIn('django.contrib.auth.middleware.AuthenticationMiddleware', settings.MIDDLEWARE)
        self.assertIn('django.middleware.locale.LocaleMiddleware', settings.MIDDLEWARE)

    def test_login_required_redirect(self):
        self.client.logout()
        response = self.client.get(reverse('task_list'))
        expected_url = f'{reverse("login")}?next={reverse("task_list")}'
        self.assertRedirects(response, expected_url)
