from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from user_app.models import User


class UserAppAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='user_profile',
            email='profile@example.com',
            password='TestPass123!'
        )

    def test_user_list_and_jwt_login_work(self):
        user_response = self.client.get(reverse('list'))
        self.assertEqual(user_response.status_code, 200)
        self.assertTrue(any(item['username'] == 'user_profile' for item in user_response.data))

        token_response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': self.user.username, 'password': 'TestPass123!'},
            format='json',
        )

        self.assertEqual(token_response.status_code, 200)
        self.assertIn('access', token_response.data)
        self.assertIn('refresh', token_response.data)
