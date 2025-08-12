from django.test import TestCase
from django.urls import reverse


class PaymentsViewsTests(TestCase):
    def test_index_ok(self):
        resp = self.client.get(reverse('payments:index'))
        self.assertEqual(resp.status_code, 200)
