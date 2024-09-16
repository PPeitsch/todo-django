from django.shortcuts import render
import logging
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView

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
