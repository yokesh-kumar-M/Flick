from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.test import override_settings
from .models import FlickUser

# Override cache to dummy to effectively bypass rate limiting during tests
@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
class AuthenticationTests(APITestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'Testpassword123',
            'display_name': 'Test User'
        }

    def test_user_registration(self):
        """Test that a new user can register successfully."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FlickUser.objects.count(), 1)
        self.assertEqual(FlickUser.objects.get().username, 'testuser')
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_user_login(self):
        """Test that an existing user can log in."""
        # Create user first
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Now try to login
        login_data = {
            'username': 'testuser',
            'password': 'Testpassword123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_invalid_login(self):
        """Test login with wrong password."""
        self.client.post(self.register_url, self.user_data, format='json')
        
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_get_profile(self):
        """Test getting the authenticated user's profile."""
        # Register and login to get token
        response = self.client.post(self.register_url, self.user_data, format='json')
        token = response.data['access_token']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        profile_url = reverse('get_profile')
        profile_response = self.client.get(profile_url)
        
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['username'], 'testuser')
