from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import BlogPost


class BlogAppTests(TestCase):
    def setUp(self):
        # Создаем двух пользователей для проверки прав доступа
        self.user1 = User.objects.create_user(username='author1', password='Password123!')
        self.user2 = User.objects.create_user(username='author2', password='Password123!')

        self.client1 = Client()
        self.client1.login(username='author1', password='Password123!')

        self.client2 = Client()
        self.client2.login(username='author2', password='Password123!')

        # Создаем тестовую запись автора 1
        self.post1 = BlogPost.objects.create(
            owner=self.user1,
            title='Первая запись автора 1',
            text='Текст первой публикации автора 1',
        )

    def test_01_anonymous_can_read_posts_but_cannot_create(self):
        """Сценарий 1: Анонимный посетитель видит публикации, но не может создавать."""
        response = self.client.get(reverse('blogs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Первая запись автора 1')
        self.assertContains(response, 'author1')
        # Ссылка на создание публикации скрыта для анонима
        self.assertNotContains(response, reverse('blogs:new_post'))

        # Попытка открыть форму создания возвращает редирект на логин
        resp_new = self.client.get(reverse('blogs:new_post'))
        self.assertEqual(resp_new.status_code, 302)
        self.assertTrue(resp_new.url.startswith(reverse('users:login')))

    def test_02_empty_blog_displays_empty_state_message(self):
        """Сценарий 2: При отсутствии записей выводится сообщение об их отсутствии."""
        BlogPost.objects.all().delete()
        response = self.client.get(reverse('blogs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Публикаций пока нет')

    def test_03_create_post_assigns_author_and_appears_first(self):
        """Сценарии 4 и 5: Создать публикацию -> автор назначается автоматически, запись первая."""
        response = self.client1.post(reverse('blogs:new_post'), {
            'title': 'Самая свежая статья',
            'text': 'Интересный контент от автора 1',
        })
        self.assertEqual(response.status_code, 302)

        new_post = BlogPost.objects.get(title='Самая свежая статья')
        self.assertEqual(new_post.owner, self.user1)

        # Проверяем главную страницу: свежая запись должна идти первой
        index_resp = self.client.get(reverse('blogs:index'))
        posts_in_context = list(index_resp.context['posts'])
        self.assertEqual(posts_in_context[0].id, new_post.id)

    def test_04_author_can_edit_own_post(self):
        """Сценарий 6: Автор может редактировать собственную запись."""
        response = self.client1.post(reverse('blogs:edit_post', args=[self.post1.id]), {
            'title': 'Измененный заголовок',
            'text': 'Измененный текст публикации',
        })
        self.assertEqual(response.status_code, 302)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, 'Измененный заголовок')
        self.assertEqual(self.post1.text, 'Измененный текст публикации')

    def test_05_other_user_can_read_but_not_edit(self):
        """Сценарии 7 и 8: Другой пользователь может читать запись, но не редактировать."""
        # Чтение доступно
        detail_resp = self.client2.get(reverse('blogs:post_detail', args=[self.post1.id]))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, 'Первая запись автора 1')
        # На странице деталей ссылка на редактирование чужой записи скрыта
        self.assertNotContains(detail_resp, reverse('blogs:edit_post', args=[self.post1.id]))

        # Попытка перейти на страницу редактирования чужой записи возвращает 404
        edit_get = self.client2.get(reverse('blogs:edit_post', args=[self.post1.id]))
        self.assertEqual(edit_get.status_code, 404)

        # Попытка отправить POST на редактирование чужой записи возвращает 404
        edit_post = self.client2.post(reverse('blogs:edit_post', args=[self.post1.id]), {
            'title': 'Попытка взлома',
            'text': 'Взломанный текст',
        })
        self.assertEqual(edit_post.status_code, 404)
        self.post1.refresh_from_db()
        self.assertNotEqual(self.post1.title, 'Попытка взлома')

    def test_06_nonexistent_post_returns_404(self):
        """Сценарий 9: Подстановка несуществующего ID возвращает 404."""
        non_existent_id = 99999
        self.assertEqual(self.client1.get(reverse('blogs:post_detail', args=[non_existent_id])).status_code, 404)
        self.assertEqual(self.client1.get(reverse('blogs:edit_post', args=[non_existent_id])).status_code, 404)
        self.assertEqual(self.client1.post(reverse('blogs:delete_post', args=[non_existent_id])).status_code, 404)

    def test_07_author_can_delete_post(self):
        """Автор может удалить публикацию с подтверждением."""
        # GET возвращает форму подтверждения
        confirm_get = self.client1.get(reverse('blogs:delete_post', args=[self.post1.id]))
        self.assertEqual(confirm_get.status_code, 200)
        self.assertContains(confirm_get, 'Удаление публикации')

        # POST удаляет публикацию
        del_post = self.client1.post(reverse('blogs:delete_post', args=[self.post1.id]))
        self.assertEqual(del_post.status_code, 302)
        self.assertFalse(BlogPost.objects.filter(id=self.post1.id).exists())

    def test_08_other_user_cannot_delete_post(self):
        """Чужой пользователь не может удалить публикацию (возврат 404)."""
        del_post = self.client2.post(reverse('blogs:delete_post', args=[self.post1.id]))
        self.assertEqual(del_post.status_code, 404)
        self.assertTrue(BlogPost.objects.filter(id=self.post1.id).exists())
