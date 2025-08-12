from django.test import TestCase
from django.urls import reverse
from .models import Broker


class BrokersViewsTests(TestCase):
    def setUp(self):
        Broker.objects.create(name='A1', is_verified=True)
        Broker.objects.create(name='B2', is_verified=False)

    def test_list_all(self):
        resp = self.client.get(reverse('brokers:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'A1')
        self.assertContains(resp, 'B2')

    def test_filter_verified_true(self):
        resp = self.client.get(reverse('brokers:list') + '?verified=1')
        self.assertContains(resp, 'A1')
        self.assertNotContains(resp, 'B2')

    def test_filter_verified_false(self):
        resp = self.client.get(reverse('brokers:list') + '?verified=0')
        self.assertContains(resp, 'B2')
        self.assertNotContains(resp, 'A1')
