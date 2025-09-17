from django.test import TestCase
from .models import Profile
from django.contrib.auth.models import User

class UserSignupTest(TestCase):
    def setUp(self):
        self.user_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'mmasiga@scoutifii.com',
            'password': 'testpassword',
            'password_confirm': 'testpassword',
        }
    def test_user_signup(self):
        response = self.client.post('/signup/', self.user_data)
        self.assertEqual(response.status_code, 302)  # Redirect to settings page
        user_exists = User.objects.filter(username='testuser').exists()
        self.assertTrue(user_exists)

    def test_user_signup_password_mismatch(self):
        self.user_data['password_confirm'] = 'wrongpassword'
        response = self.client.post('/signup/', self.user_data)
        self.assertEqual(response.status_code, 302)

class UserSProfileTest(TestCase):
    def setUp(self):
        self.profile_data = {
            'bio': 'my biography',
            'location': 'my location',
            'phone_no': '0700101010',
            'country_id': 'Uganda',
            'profile_type_data': 'User',
            'birth_date': '1990/01/01'
        }
    def test_user_profile(self):
        response = self.client.post('/settings/', self.profile_data)
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard page
        profile_exists = Profile.objects.filter(phone_no='0700101010').exists()
        self.assertFalse(profile_exists)


