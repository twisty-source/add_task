from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UsersAppTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход в систему')

    def test_register_page_renders(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Регистрация')

    def test_user_can_login(self):
        User.objects.create_user(username='testlogin', password='SecurePass123!')
        response = self.client.post(reverse('users:login'), {
            'username': 'testlogin',
            'password': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)
