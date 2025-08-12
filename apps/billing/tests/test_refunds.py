from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.billing.models import Plan, Purchase, CreditTransaction, CreditWallet, ConsumptionEvent, ServiceType
from apps.billing.selectors import get_wallet_for_user
from apps.billing.services.stripe_service import _credit_wallet, request_refund


@override_settings(BILLING_REFUND_PRO_RATA=True, BILLING_ALLOW_REFUND_IF_USED_THRESHOLD=0)
class BillingRefundTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='refund', password='pass')
        self.plan = Plan.objects.create(name='Pro', slug='pro', price_usd=100, credits_on_purchase=10, renewal_interval=Plan.INTERVAL_ONE_OFF)
        self.purchase = Purchase.objects.create(user=self.user, plan=self.plan, amount_usd=100, credits_granted=10, status=Purchase.STATUS_PAID)
        self.purchase.open_guarantee()
        # dar créditos como si se completó checkout
        _credit_wallet(self.user, 10, 'init', {'purchase_id': self.purchase.id})
        ServiceType.objects.create(code='exam', label='Exam', default_cost_credits=1)

    def test_full_refund_no_usage(self):
        # sin consumo
        amount = request_refund(self.user, self.purchase)
        self.assertEqual(amount, 100)

    def test_prorata_with_usage(self):
        # consumir 4 de 10 -> prorrata 60
        w = get_wallet_for_user(self.user)
        ConsumptionEvent.objects.create(wallet=w, service_type=ServiceType.objects.get(code='exam'), credits_spent=4)
        amount = request_refund(self.user, self.purchase)
        self.assertEqual(amount, 60)
