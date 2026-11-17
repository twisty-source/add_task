"""Схемы URL для приложения blogs."""
from django.urls import path
from . import views

app_name = 'blogs'
urlpatterns = [
    # Главная страница со всеми публикациями
    path('', views.index, name='index'),
    # Отдельная страница публикации
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Создание публикации
    path('posts/new/', views.new_post, name='new_post'),
    # Редактирование публикации
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    # Удаление публикации
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
]
