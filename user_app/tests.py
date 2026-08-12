from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from api_config import api_url

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model creation and validation"""

    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_creation(self):
        """Test user is created successfully"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_email_unique(self):
        """Test email uniqueness constraint"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='another_user',
                email='test@example.com',
                password='testpass123'
            )

    def test_user_with_profile_pic(self):
        """Test user can have profile picture URL"""
        user = User.objects.create_user(
            username='pictureuser',
            email='picture@example.com',
            password='testpass123',
            profile_pic_url='https://example.com/pic.jpg'
        )
        self.assertEqual(user.profile_pic_url, 'https://example.com/pic.jpg')

    def test_user_profile_pic_optional(self):
        """Test profile picture is optional"""
        user = User.objects.create_user(
            username='nopicuser',
            email='nopic@example.com',
            password='testpass123'
        )
        self.assertIsNone(user.profile_pic_url)

    def test_user_full_name(self):
        """Test user full name property"""
        self.assertEqual(self.user.get_full_name(), 'Test User')

    def test_user_str(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'testuser')


class UserListAPITest(APITestCase):
    """Test User list endpoint"""

    def setUp(self):
        """Create test users"""
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            first_name='First',
            last_name='User'
        )
        User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            first_name='Second',
            last_name='User'
        )

    def test_list_all_users(self):
        """Test listing all users"""
        response = self.client.get(api_url('users/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_list_contains_required_fields(self):
        """Test user list response contains required fields"""
        response = self.client.get(api_url('users/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data[0]
        self.assertIn('username', user_data)
        self.assertIn('email', user_data)
        self.assertIn('first_name', user_data)
        self.assertIn('last_name', user_data)

    def test_user_list_empty(self):
        """Test user list when no users exist"""
        User.objects.all().delete()
        response = self.client.get(api_url('users/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_users_count(self):
        """Test correct number of users in response"""
        response = self.client.get(api_url('users/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['username'], 'user1')
        self.assertEqual(response.data[1]['username'], 'user2')

    def test_user_list_password_not_exposed(self):
        """Test that password is not exposed in API response"""
        response = self.client.get(api_url('users/'))
        user_data = response.data[0]
        self.assertNotIn('password', user_data)
