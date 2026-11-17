from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    """Модель задачи пользователя."""
    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Низкий'),
        (PRIORITY_NORMAL, 'Обычный'),
        (PRIORITY_HIGH, 'Высокий'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Срок выполнения')
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_NORMAL,
        verbose_name='Приоритет',
    )
    completed = models.BooleanField(default=False, verbose_name='Выполнено')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['completed', '-date_added']

    def __str__(self):
        """Возвращает строковое представление задачи."""
        return self.title

    @property
    def is_overdue(self):
        """Проверяет, просрочена ли невыполненная задача."""
        if self.due_date and not self.completed:
            return self.due_date < timezone.now()
        return False
