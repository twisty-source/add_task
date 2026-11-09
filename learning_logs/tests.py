from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Topic, Entry


class LearningLogTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.client1 = Client()
        self.client1.login(username='user1', password='password123')
        self.client2 = Client()
        self.client2.login(username='user2', password='password123')

        self.topic1 = Topic.objects.create(text='Topic 1 by user1', owner=self.user1)
        self.entry1 = Entry.objects.create(topic=self.topic1, text='Entry 1 for topic 1')

    def test_index_page_accessible(self):
        response = self.client.get(reverse('learning_logs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Learning Log')

    def test_topics_login_required(self):
        response = self.client.get(reverse('learning_logs:topics'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('users:login')))

    def test_user_can_view_own_topics(self):
        response = self.client1.get(reverse('learning_logs:topics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Topic 1 by user1')

    def test_user_cannot_view_other_users_topics_in_list(self):
        response = self.client2.get(reverse('learning_logs:topics'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Topic 1 by user1')

    def test_user_cannot_view_other_users_topic_detail(self):
        response = self.client2.get(reverse('learning_logs:topic', args=[self.topic1.id]))
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_edit_other_users_entry(self):
        response = self.client2.get(reverse('learning_logs:edit_entry', args=[self.entry1.id]))
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_add_entry_to_other_users_topic(self):
        response = self.client2.post(
            reverse('learning_logs:new_entry', args=[self.topic1.id]),
            {'text': 'Hacked entry'}
        )
        self.assertEqual(response.status_code, 404)

    def test_user_can_create_topic(self):
        response = self.client1.post(reverse('learning_logs:new_topic'), {'text': 'New Test Topic'})
        self.assertEqual(response.status_code, 302)
        new_topic = Topic.objects.get(text='New Test Topic')
        self.assertEqual(new_topic.owner, self.user1)

    def test_user_can_create_entry(self):
        response = self.client1.post(
            reverse('learning_logs:new_entry', args=[self.topic1.id]),
            {'text': 'New entry text'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Entry.objects.filter(text='New entry text').exists())

    def test_user_can_edit_entry(self):
        response = self.client1.post(
            reverse('learning_logs:edit_entry', args=[self.entry1.id]),
            {'text': 'Updated entry text'}
        )
        self.assertEqual(response.status_code, 302)
        self.entry1.refresh_from_db()
        self.assertEqual(self.entry1.text, 'Updated entry text')
