from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class UsersBlogTests(TestCase):
    def test_registration_creates_user_and_logs_in(self):
        """Сценарий 3: Зарегистрироваться -> создан пользователь и выполнен вход."""
        response = self.client.post(reverse('users:register'), {
            'username': 'newauthor',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newauthor').exists())

        # Проверяем отображение имени вошедшего пользователя на главной странице
        follow_resp = self.client.get(reverse('blogs:index'))
        self.assertContains(follow_resp, 'newauthor')

    def test_logout_via_post_ends_session(self):
        """Сценарий 10: Выход через POST-форму завершает сеанс."""
        user = User.objects.create_user(username='loggeduser', password='Password123!')
        client = Client()
        client.login(username='loggeduser', password='Password123!')

        resp = client.post(reverse('users:logout'))
        self.assertEqual(resp.status_code, 302)

        # После выхода анонимный пользователь видит ссылку "Войти"
        index_resp = client.get(reverse('blogs:index'))
        self.assertContains(index_resp, 'Войти')
        self.assertNotContains(index_resp, 'loggeduser')

    def test_logout_via_get_does_not_log_out_or_returns_405(self):
        """Сценарий 11: GET-запрос на адрес выхода не завершает сеанс (в Django 5.2 возвращает 405)."""
        user = User.objects.create_user(username='getlogoutuser', password='Password123!')
        client = Client()
        client.login(username='getlogoutuser', password='Password123!')

        resp = client.get(reverse('users:logout'))
        # В Django 5.2 LogoutView по умолчанию отклоняет GET-запросы со статусом 405
        self.assertEqual(resp.status_code, 405)

        # Проверяем, что пользователь остался авторизован
        index_resp = client.get(reverse('blogs:index'))
        self.assertContains(index_resp, 'getlogoutuser')

    def test_login_page_renders(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход в аккаунт автора')
