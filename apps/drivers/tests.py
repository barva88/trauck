from django.test import TestCase
from django.urls import reverse


class DriversViewsTests(TestCase):
    def test_index_ok(self):
        resp = self.client.get(reverse('drivers:index'))
        self.assertEqual(resp.status_code, 200)
