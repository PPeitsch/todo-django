import logging
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy
import logging
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect


logger = logging.getLogger(__name__)


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'authentication/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        logger.info(f"New user created: {self.object.username}")
        return response


class CustomLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'authentication/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f"User logged in: {self.request.user.username}")
        return response

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect('home')  # o 'login' si prefieres redirigir al login

    def post(self, request):
        return self.get(request)
