from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField, F
from django.utils import timezone
from .models import Task
from .forms import TaskForm


def index(request):
    """Главная страница приложения."""
    total_tasks = 0
    active_tasks = 0
    if request.user.is_authenticated:
        user_tasks = Task.objects.filter(owner=request.user)
        total_tasks = user_tasks.count()
        active_tasks = user_tasks.filter(completed=False).count()
    context = {
        'total_tasks': total_tasks,
        'active_tasks': active_tasks,
    }
    return render(request, 'tasks/index.html', context)


@login_required
def task_list(request):
    """Выводит список задач текущего пользователя."""
    tasks = Task.objects.filter(owner=request.user)

    # Фильтрация (дополнительное задание)
    filter_by = request.GET.get('filter', 'all')
    now = timezone.now()

    if filter_by == 'active':
        tasks = tasks.filter(completed=False)
    elif filter_by == 'completed':
        tasks = tasks.filter(completed=True)
    elif filter_by == 'overdue':
        tasks = tasks.filter(completed=False, due_date__lt=now)

    # Поиск по названию и описанию
    search_query = request.GET.get('q', '').strip()
    if search_query:
        tasks = tasks.filter(title__icontains=search_query) | tasks.filter(description__icontains=search_query)

    # Рекомендуемый порядок:
    # 1. Невыполненные перед выполненными
    # 2. Высокий приоритет перед обычным и низким
    # 3. Ближайший срок выполнения (без срока — в конце)
    # 4. Дата добавления
    priority_order = Case(
        When(priority='high', then=Value(1)),
        When(priority='normal', then=Value(2)),
        When(priority='low', then=Value(3)),
        default=Value(4),
        output_field=IntegerField(),
    )

    tasks = tasks.order_by(
        'completed',
        priority_order,
        F('due_date').asc(nulls_last=True),
        '-date_added',
    )

    context = {
        'tasks': tasks,
        'current_filter': filter_by,
        'search_query': search_query,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def new_task(request):
    """Создает новую задачу для текущего пользователя."""
    if request.method != 'POST':
        form = TaskForm()
    else:
        form = TaskForm(data=request.POST)
        if form.is_valid():
            new_task_obj = form.save(commit=False)
            new_task_obj.owner = request.user
            new_task_obj.save()
            return redirect('tasks:task_list')

    context = {'form': form}
    return render(request, 'tasks/new_task.html', context)


@login_required
def edit_task(request, task_id):
    """Редактирует задачу текущего пользователя."""
    task = get_object_or_404(Task, id=task_id, owner=request.user)

    if request.method != 'POST':
        form = TaskForm(instance=task)
    else:
        form = TaskForm(instance=task, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('tasks:task_list')

    context = {'task': task, 'form': form}
    return render(request, 'tasks/edit_task.html', context)


@login_required
def delete_task(request, task_id):
    """Удаляет задачу после подтверждения (только методом POST)."""
    task = get_object_or_404(Task, id=task_id, owner=request.user)

    if request.method == 'POST':
        task.delete()
        return redirect('tasks:task_list')

    context = {'task': task}
    return render(request, 'tasks/delete_confirm.html', context)


@login_required
def toggle_task(request, task_id):
    """Переключает статус выполнения задачи (только методом POST)."""
    task = get_object_or_404(Task, id=task_id, owner=request.user)

    if request.method == 'POST':
        task.completed = not task.completed
        task.save()

    return redirect('tasks:task_list')
