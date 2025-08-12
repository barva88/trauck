from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.billing.models import ServiceType
from apps.billing.selectors import get_wallet_for_user
from apps.billing.services.stripe_service import debit_credits, current_balance


class BillingServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='svc', password='pass')
        self.wallet = get_wallet_for_user(self.user)
        self.wallet.balance = 5
        self.wallet.save(update_fields=['balance'])
        ServiceType.objects.create(code='exam', label='Exam', default_cost_credits=1)

    def test_debit_and_balance(self):
        self.assertEqual(current_balance(self.user), 5)
        ok = debit_credits(self.user, 'exam', 2, {'source': 'test'})
        self.assertTrue(ok)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 3)
        self.assertEqual(self.wallet.consumptions.count(), 1)
