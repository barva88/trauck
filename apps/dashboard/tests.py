from django.test import TestCase
from django.urls import reverse


class SmokeTests(TestCase):
    def test_admin_login_page_loads(self):
        resp = self.client.get('/admin/login/?next=/admin/')
        self.assertEqual(resp.status_code, 200)

# Create your tests here.
