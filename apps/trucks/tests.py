from django.test import TestCase
from django.urls import reverse


class TrucksViewsTests(TestCase):
    def test_index_ok(self):
        resp = self.client.get(reverse('trucks:index'))
        self.assertEqual(resp.status_code, 200)
