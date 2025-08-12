from django.test import TestCase
from django.urls import reverse


class PagesViewsTests(TestCase):
    def test_dashboard_ok(self):
        resp = self.client.get(reverse('pages:index'))
        self.assertEqual(resp.status_code, 200)
        # El template incluye el segmento 'dashboard'
        self.assertContains(resp, 'dashboard')
