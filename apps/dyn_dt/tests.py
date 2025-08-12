from django.test import TestCase
from django.urls import reverse


class DynDTTests(TestCase):
    def test_index(self):
        resp = self.client.get(reverse('dynamic_dt'))
        self.assertEqual(resp.status_code, 200)
