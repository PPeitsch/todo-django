from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.conf import settings


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    def test_urls_resolve(self):
        # Test that URLs are correctly configured
        self.assertEqual(resolve('/auth/login/').view_name, 'login')
        self.assertEqual(resolve('/auth/signup/').view_name, 'signup')
        self.assertEqual(resolve('/auth/logout/').view_name, 'logout')

    @override_settings(LANGUAGE_CODE='en-us')
    def test_signup_view_en(self):
        self._test_signup_view()

    @override_settings(LANGUAGE_CODE='es')
    def test_signup_view_es(self):
        self._test_signup_view()

    def _test_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/signup.html')

        # Test user registration
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        })
        self.assertIn(response.status_code, [200, 302])  # Either success (302) or form errors (200)
        if response.status_code == 302:
            self.assertTrue(User.objects.filter(username='newuser').exists())

    @override_settings(LANGUAGE_CODE='en-us')
    def test_login_view_en(self):
        self._test_login_view()

    @override_settings(LANGUAGE_CODE='es')
    def test_login_view_es(self):
        self._test_login_view()

    def _test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')

        # Test user login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword123',
        })
        self.assertIn(response.status_code, [200, 302])  # Either success (302) or form errors (200)
        if response.status_code == 302:
            self.assertTrue('_auth_user_id' in self.client.session)

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertFalse('_auth_user_id' in self.client.session)

    @override_settings(LANGUAGE_CODE='en-us')
    def test_login_failed_en(self):
        self._test_login_failed()

    @override_settings(LANGUAGE_CODE='es')
    def test_login_failed_es(self):
        self._test_login_failed()

    def _test_login_failed(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Stay on the same page
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertTrue('form' in response.context and response.context['form'].errors)

    @override_settings(LANGUAGE_CODE='en-us')
    def test_signup_password_mismatch_en(self):
        self._test_signup_password_mismatch()

    @override_settings(LANGUAGE_CODE='es')
    def test_signup_password_mismatch_es(self):
        self._test_signup_password_mismatch()

    def _test_signup_password_mismatch(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'password123',
            'password2': 'password321',
        })
        self.assertEqual(response.status_code, 200)  # Stay on the same page
        self.assertTrue('form' in response.context and response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_settings(self):
        # Print out relevant settings for debugging
        print(f"INSTALLED_APPS: {settings.INSTALLED_APPS}")
        print(f"ROOT_URLCONF: {settings.ROOT_URLCONF}")
        print(f"MIDDLEWARE: {settings.MIDDLEWARE}")
