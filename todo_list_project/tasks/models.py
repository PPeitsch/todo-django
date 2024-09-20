from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    completed = models.BooleanField(_('completed'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', verbose_name=_('user'))

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('task')
        verbose_name_plural = _('tasks')
