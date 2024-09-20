import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Task
from .forms import TaskForm

logger = logging.getLogger(__name__)


def home(request):
    logger.info(_("User %(user)s accessed the home page") % {'user': request.user})
    return render(request, 'tasks/home.html')


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    query = request.GET.get('query')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if date_from:
        tasks = tasks.filter(created_at__gte=date_from)
    if date_to:
        tasks = tasks.filter(created_at__lte=date_to)

    logger.info(_("User %(user)s viewed their task list") % {'user': request.user})
    return render(request, 'tasks/tasks_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            logger.info(_("User %(user)s created a new task: %(task)s") % {'user': request.user, 'task': task.title})
            messages.success(request, _('Task was created successfully.'))
            return redirect('task_list')
        else:
            logger.warning(_("User %(user)s attempted to create a task with invalid data") % {'user': request.user})
    else:
        form = TaskForm()
    return render(request, 'tasks/tasks_form.html', {'form': form})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            logger.info(_("User %(user)s updated task: %(task)s") % {'user': request.user, 'task': task.title})
            messages.success(request, _('Task was updated successfully.'))
            return redirect('task_list')
        else:
            logger.warning(
                _("User %(user)s attempted to update task %(task)s with invalid data") % {'user': request.user,
                                                                                          'task': task.title})
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/tasks_form.html', {'form': form})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        logger.info(_("User %(user)s deleted task: %(task)s") % {'user': request.user, 'task': task.title})
        task.delete()
        messages.success(request, _('Task was deleted successfully.'))
        return redirect('task_list')
    return render(request, 'tasks/tasks_confirm_delete.html', {'task': task})


@login_required
def task_toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    status = _('completed') if task.completed else _('incomplete')
    logger.info(_("User %(user)s marked task: %(task)s as %(status)s") % {'user': request.user, 'task': task.title,
                                                                          'status': status})
    return redirect('task_list')
