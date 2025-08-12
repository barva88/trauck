from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class EducationDashboardTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='bob', password='pass')

    def test_requires_login(self):
        resp = self.client.get(reverse('education:dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/accounts/login', resp['Location'])

    def test_ok_when_logged_in(self):
        self.client.login(username='bob', password='pass')
        resp = self.client.get(reverse('education:dashboard'))
        self.assertEqual(resp.status_code, 200)
