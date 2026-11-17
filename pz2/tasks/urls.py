"""Схемы URL для приложения tasks."""
from django.urls import path
from . import views

app_name = 'tasks'
urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    # Список задач
    path('tasks/', views.task_list, name='task_list'),
    # Создание новой задачи
    path('tasks/new/', views.new_task, name='new_task'),
    # Редактирование задачи
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    # Удаление задачи
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    # Переключение статуса выполнения задачи
    path('tasks/<int:task_id>/toggle/', views.toggle_task, name='toggle_task'),
]
