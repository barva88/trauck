from django.test import TestCase
from django.urls import reverse


class NotificationsViewsTests(TestCase):
    def test_index_ok(self):
        resp = self.client.get(reverse('notifications:index'))
        self.assertEqual(resp.status_code, 200)
