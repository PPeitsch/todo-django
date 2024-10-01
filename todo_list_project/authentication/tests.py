from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.conf import settings
from django.utils.translation import activate


class AuthenticationTests(TestCase):
    """
    Test case for authentication functionality.

    This class contains tests to verify various aspects of the authentication system,
    including URL resolution, signup, login, logout, and internationalization.
    """

    def setUp(self):
        """
        Set up data for each test.

        This method is called before each test method to set up any objects that
        may be modified by the test.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    def test_urls_resolve(self):
        """
        Test that authentication URLs resolve correctly for both Spanish and English.

        This test verifies that the login, signup, and logout URLs resolve to the correct view names
        in both Spanish and English language settings.
        """
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
        """
        Test the signup view functionality in English.

        This test verifies that the signup process works correctly when the language is set to English.
        """
        activate('en')
        self._test_signup_view()

    @override_settings(LANGUAGE_CODE='es')
    def test_signup_view_es(self):
        """
        Test the signup view functionality in Spanish.

        This test verifies that the signup process works correctly when the language is set to Spanish.
        """
        activate('es')
        self._test_signup_view()

    def _test_signup_view(self):
        """
        Helper method to test the signup view functionality.

        This method tests the signup process, including successful registration and
        handling of duplicate usernames.
        """
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
        """
        Test the login view functionality.

        This test verifies that users can successfully log in and that the login process
        creates the appropriate session data.
        """
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
        """
        Test the logout view functionality.

        This test verifies that users can successfully log out and that the logout process
        removes the appropriate session data.
        """
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_authenticated_user_redirect(self):
        """
        Test redirection for authenticated users.

        This test verifies that authenticated users are redirected to the home page
        when they try to access the login or signup pages.
        """
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('home'))
        response = self.client.get(reverse('signup'))
        self.assertRedirects(response, reverse('home'))

    def test_unauthenticated_user_access(self):
        """
        Test access for unauthenticated users.

        This test verifies that unauthenticated users can access the login and signup pages.
        """
        self.client.logout()
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_language_in_url(self):
        """
        Test that the correct language code is present in URLs.

        This test verifies that the appropriate language code is included in the URL
        for both English and Spanish versions of the login and signup pages.
        """
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
        """
        Test handling of password mismatch during signup in English.

        This test verifies that the signup process correctly handles cases where
        the two entered passwords do not match, when the language is set to English.
        """
        activate('en')
        self._test_signup_password_mismatch()

    @override_settings(LANGUAGE_CODE='es')
    def test_signup_password_mismatch_es(self):
        """
        Test handling of password mismatch during signup in Spanish.

        This test verifies that the signup process correctly handles cases where
        the two entered passwords do not match, when the language is set to Spanish.
        """
        activate('es')
        self._test_signup_password_mismatch()

    def _test_signup_password_mismatch(self):
        """
        Helper method to test password mismatch during signup.

        This method tests that the signup process correctly handles and reports
        cases where the two entered passwords do not match.
        """
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'password123',
            'password2': 'password321',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context and response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_settings_configuration(self):
        """
        Test the Django settings configuration.

        This test verifies that the necessary apps and middleware are included
        in the Django settings for proper authentication functionality.
        """
        self.assertIn('django.contrib.auth', settings.INSTALLED_APPS)
        self.assertIn('authentication.apps.AuthenticationConfig', settings.INSTALLED_APPS)
        self.assertEqual(settings.ROOT_URLCONF, 'todo_list_project.urls')
        self.assertIn('django.middleware.security.SecurityMiddleware', settings.MIDDLEWARE)
        self.assertIn('django.contrib.auth.middleware.AuthenticationMiddleware', settings.MIDDLEWARE)
        self.assertIn('django.middleware.locale.LocaleMiddleware', settings.MIDDLEWARE)

    def test_login_required_redirect(self):
        """
        Test redirection for login-required views.

        This test verifies that unauthenticated users are redirected to the login page
        when they try to access a view that requires authentication.
        """
        self.client.logout()
        response = self.client.get(reverse('task_list'))
        expected_url = f'{reverse("login")}?next={reverse("task_list")}'
        self.assertRedirects(response, expected_url)