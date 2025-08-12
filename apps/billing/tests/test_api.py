from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.billing.models import Plan


class BillingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username='bill', password='pass')
        self.plan = Plan.objects.create(name='Plan A', slug='plan-a', price_usd=10, credits_on_purchase=10, renewal_interval=Plan.INTERVAL_ONE_OFF)

    def test_list_plans(self):
        url = reverse('billing:plans')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json()) >= 1)

    def test_wallet_requires_auth(self):
        url = reverse('billing:wallet')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)
        self.client.login(username='bill', password='pass')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
