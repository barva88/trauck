from django.test import TestCase
from django.urls import reverse


class AccountsViewsTests(TestCase):
    def test_index_ok(self):
        url = reverse('accounts:index')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
