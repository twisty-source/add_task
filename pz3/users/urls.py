"""Определяет схемы URL для пользователей."""
from django.urls import path, include
from . import views

app_name = 'users'
urlpatterns = [
    # Стандартные URL аутентификации (login, logout)
    path('', include('django.contrib.auth.urls')),
    # Регистрация
    path('register/', views.register, name='register'),
]
