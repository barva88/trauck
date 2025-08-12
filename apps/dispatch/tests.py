from django.test import TestCase
from django.urls import reverse


class DispatchViewsTests(TestCase):
    def test_index_ok(self):
        resp = self.client.get(reverse('dispatch:index'))
        self.assertEqual(resp.status_code, 200)
