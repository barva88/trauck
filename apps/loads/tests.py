from django.test import TestCase
from django.urls import reverse
from datetime import date
from apps.brokers.models import Broker
from apps.carriers.models import Carrier
from .models import Load


class LoadsViewsTests(TestCase):
    def setUp(self):
        self.broker = Broker.objects.create(name='BrokerX')
        self.carrier = Carrier.objects.create(name='CarrierY', dot_number='DOT123', mc_number='MC123')
        self.load = Load.objects.create(
            broker=self.broker,
            carrier=self.carrier,
            origin='NY',
            destination='LA',
            pickup_date=date(2025, 8, 1),
            delivery_date=date(2025, 8, 5),
            status='pending',
            rate=1000,
        )

    def test_list(self):
        resp = self.client.get(reverse('loads:index'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'NY')

    def test_detail(self):
        resp = self.client.get(reverse('loads:detail', args=[self.load.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'NY')
