import logging
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'authentication/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        logger.info(_("New user created: %(username)s") % {'username': self.object.username})
        return response


class CustomLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'authentication/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(_("User logged in: %(username)s") % {'username': self.request.user.username})
        return response


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, _("You have been successfully logged out."))
        return redirect('home')

    def post(self, request):
        return self.get(request)
