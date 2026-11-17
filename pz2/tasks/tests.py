from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Task


class TaskManagerTests(TestCase):
    def setUp(self):
        # Создаем двух пользователей для проверки изоляции данных
        self.user1 = User.objects.create_user(username='user1', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', password='Password123!')

        self.client1 = Client()
        self.client1.login(username='user1', password='Password123!')

        self.client2 = Client()
        self.client2.login(username='user2', password='Password123!')

        # Создаем задачу для user1
        self.task1 = Task.objects.create(
            owner=self.user1,
            title='Задача 1 от user1',
            description='Подробное описание 1',
            priority=Task.PRIORITY_NORMAL,
            completed=False,
            due_date=timezone.now() + timedelta(days=2),
        )

    def test_01_anonymous_redirected_to_login(self):
        """Сценарий 1: Открыть /tasks/ без входа -> редирект на логин."""
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('users:login')))

        response_new = self.client.get(reverse('tasks:new_task'))
        self.assertEqual(response_new.status_code, 302)
        self.assertTrue(response_new.url.startswith(reverse('users:login')))

    def test_02_registration_creates_user_and_logs_in(self):
        """Сценарий 2: Зарегистрироваться -> пользователь создан и выполнен вход."""
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'password1': 'StrongPass999!',
            'password2': 'StrongPass999!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # Пользователь должен быть авторизован и перенаправлен на список задач
        self.assertEqual(response.url, reverse('tasks:task_list'))

    def test_03_create_task_assigns_owner_and_appears_only_for_creator(self):
        """Сценарий 3: Создать задачу -> привязывается к создателю и видна только ему."""
        response = self.client1.post(reverse('tasks:new_task'), {
            'title': 'Новая супер задача',
            'description': 'Описание новой задачи',
            'priority': Task.PRIORITY_HIGH,
        })
        self.assertEqual(response.status_code, 302)
        new_task = Task.objects.get(title='Новая супер задача')
        self.assertEqual(new_task.owner, self.user1)

        # Проверяем, что задача видна в списке user1
        response1 = self.client1.get(reverse('tasks:task_list'))
        self.assertContains(response1, 'Новая супер задача')

        # Проверяем, что задача НЕ видна в списке user2
        response2 = self.client2.get(reverse('tasks:task_list'))
        self.assertNotContains(response2, 'Новая супер задача')

    def test_04_edit_task_updates_priority_and_due_date(self):
        """Сценарий 4: Изменить срок и приоритет -> новые данные сохраняются."""
        new_due = timezone.now() + timedelta(days=5)
        due_str = new_due.strftime('%Y-%m-%dT%H:%M')

        response = self.client1.post(reverse('tasks:edit_task', args=[self.task1.id]), {
            'title': 'Обновленное название',
            'description': 'Обновленное описание',
            'priority': Task.PRIORITY_HIGH,
            'due_date': due_str,
            'completed': False,
        })
        self.assertEqual(response.status_code, 302)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Обновленное название')
        self.assertEqual(self.task1.priority, Task.PRIORITY_HIGH)

    def test_05_toggle_task_to_completed(self):
        """Сценарий 5: Отметить задачу выполненной -> состояние меняется."""
        self.assertFalse(self.task1.completed)
        response = self.client1.post(reverse('tasks:toggle_task', args=[self.task1.id]))
        self.assertEqual(response.status_code, 302)
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.completed)

    def test_06_toggle_task_back_to_active(self):
        """Сценарий 6: Вернуть задачу в работу -> состояние снова активное."""
        self.task1.completed = True
        self.task1.save()

        response = self.client1.post(reverse('tasks:toggle_task', args=[self.task1.id]))
        self.assertEqual(response.status_code, 302)
        self.task1.refresh_from_db()
        self.assertFalse(self.task1.completed)

    def test_07_user_sees_only_own_tasks(self):
        """Сценарий 7: Задачи первого пользователя не видны второму."""
        response1 = self.client1.get(reverse('tasks:task_list'))
        self.assertContains(response1, self.task1.title)

        response2 = self.client2.get(reverse('tasks:task_list'))
        self.assertNotContains(response2, self.task1.title)

    def test_08_forbidden_access_to_other_users_task(self):
        """Сценарий 8: Подставить ID чужой задачи -> 404, данные не меняются."""
        # Чужое редактирование через GET
        resp_edit_get = self.client2.get(reverse('tasks:edit_task', args=[self.task1.id]))
        self.assertEqual(resp_edit_get.status_code, 404)

        # Чужое редактирование через POST
        resp_edit_post = self.client2.post(reverse('tasks:edit_task', args=[self.task1.id]), {
            'title': 'Взлом',
            'priority': Task.PRIORITY_LOW,
        })
        self.assertEqual(resp_edit_post.status_code, 404)
        self.task1.refresh_from_db()
        self.assertNotEqual(self.task1.title, 'Взлом')

        # Чужое удаление через POST
        resp_del = self.client2.post(reverse('tasks:delete_task', args=[self.task1.id]))
        self.assertEqual(resp_del.status_code, 404)
        self.assertTrue(Task.objects.filter(id=self.task1.id).exists())

        # Чужое переключение статуса
        resp_toggle = self.client2.post(reverse('tasks:toggle_task', args=[self.task1.id]))
        self.assertEqual(resp_toggle.status_code, 404)

    def test_09_nonexistent_task_returns_404(self):
        """Сценарий 9: Несуществующий ID возвращает 404, сервер не падает с 500."""
        non_existent_id = 999999
        self.assertEqual(self.client1.get(reverse('tasks:edit_task', args=[non_existent_id])).status_code, 404)
        self.assertEqual(self.client1.get(reverse('tasks:delete_task', args=[non_existent_id])).status_code, 404)
        self.assertEqual(self.client1.post(reverse('tasks:toggle_task', args=[non_existent_id])).status_code, 404)

    def test_10_delete_task_after_confirmation(self):
        """Сценарий 10: После подтверждения задача удаляется."""
        # Страница подтверждения GET отображает форму и детали задачи
        confirm_get = self.client1.get(reverse('tasks:delete_task', args=[self.task1.id]))
        self.assertEqual(confirm_get.status_code, 200)
        self.assertContains(confirm_get, 'Подтверждение удаления')

        # POST-запрос удаляет задачу
        del_post = self.client1.post(reverse('tasks:delete_task', args=[self.task1.id]))
        self.assertEqual(del_post.status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    def test_11_get_request_does_not_delete_task(self):
        """Сценарий 11: Отправить запрос на удаление методом GET -> задача НЕ удаляется."""
        self.client1.get(reverse('tasks:delete_task', args=[self.task1.id]))
        self.assertTrue(Task.objects.filter(id=self.task1.id).exists())

    def test_12_logout_via_post_ends_session(self):
        """Сценарий 12: POST-выход завершает сеанс."""
        response = self.client1.post(reverse('users:logout'))
        # В Django 5 logout перенаправляет на LOGOUT_REDIRECT_URL ('tasks:index')
        self.assertEqual(response.status_code, 302)
        # Проверяем, что теперь пользователь анонимен
        list_resp = self.client1.get(reverse('tasks:task_list'))
        self.assertEqual(list_resp.status_code, 302)
        self.assertTrue(list_resp.url.startswith(reverse('users:login')))

    def test_13_overdue_property(self):
        """Проверка работы свойства is_overdue для просроченных задач."""
        overdue_task = Task.objects.create(
            owner=self.user1,
            title='Старая задача',
            due_date=timezone.now() - timedelta(days=2),
            completed=False,
        )
        self.assertTrue(overdue_task.is_overdue)

        # Выполненная задача не считается просроченной
        overdue_task.completed = True
        overdue_task.save()
        self.assertFalse(overdue_task.is_overdue)
