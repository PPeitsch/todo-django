import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Task
from .forms import TaskForm

logger = logging.getLogger(__name__)


def home(request):
    logger.info(f"Usuario {request.user} accedió a la página de inicio")
    return render(request, 'tasks/home.html')


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    query = request.GET.get('query')
    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        logger.info(f"Usuario {request.user} buscó tareas con la consulta: {query}")
    else:
        logger.info(f"Usuario {request.user} visualizó su lista de tareas")
    return render(request, 'tasks/tasks_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            logger.info(f"Usuario {request.user} creó una nueva tarea: {task.title}")
            messages.success(request, 'La tarea fue creada exitosamente.')
            return redirect('task_list')
        else:
            logger.warning(f"Usuario {request.user} intentó crear una tarea con datos inválidos")
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
            logger.info(f"Usuario {request.user} actualizó la tarea: {task.title}")
            messages.success(request, 'La tarea fue actualizada exitosamente.')
            return redirect('task_list')
        else:
            logger.warning(f"Usuario {request.user} intentó actualizar la tarea {task.title} con datos inválidos")
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/tasks_form.html', {'form': form})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        logger.info(f"Usuario {request.user} eliminó la tarea: {task.title}")
        task.delete()
        messages.success(request, 'La tarea fue eliminada exitosamente.')
        return redirect('task_list')
    return render(request, 'tasks/tasks_confirm_delete.html', {'task': task})


@login_required
def task_toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    logger.info(
        f"Usuario {request.user} cambió el estado de la tarea: {task.title}. Nuevo estado: {'Completada' if task.completed else 'Incompleta'}")
    return redirect('task_list')
