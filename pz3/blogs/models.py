from django.db import models
from django.contrib.auth.models import User


class BlogPost(models.Model):
    """Модель публикации в блоге."""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст публикации')
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-date_added']

    def __str__(self):
        """Возвращает строковое представление публикации."""
        return self.title
