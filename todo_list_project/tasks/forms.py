from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'title': _('Title'),
            'description': _('Description'),
            'completed': _('Completed'),
        }
