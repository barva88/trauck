from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from apps.billing.models import Plan, Purchase, CreditTransaction
from apps.billing.services.stripe_service import create_checkout_session, handle_checkout_completed
from django.conf import settings
from unittest.mock import patch
import stripe

User = get_user_model()

@override_settings(STRIPE_SECRET_KEY='sk_test_dummy')
class BillingCreditsTests(TestCase):
    def setUp(self):
        # Some UserManagers require username positional; provide both for compatibility
        try:
            self.user = User.objects.create_user('testuser', email='testuser@example.com', password='pass')
        except TypeError:
            self.user = User.objects.create_user(email='testuser@example.com', password='pass')

    def test_checkout_grants_credits_when_plan_has_credits(self):
        plan = Plan.objects.create(name='Test Plan', slug='test-plan', price_usd=10, credits_on_purchase=5, renewal_interval=Plan.INTERVAL_ONE_OFF, stripe_price_id='price_test')
        # Mock stripe customer and session creation
        with patch('stripe.Customer.create') as m_cust, patch('stripe.checkout.Session.create') as m_sess:
            m_cust.return_value = type('O', (), {'id': 'cus_test'})()
            m_sess.return_value = type('O', (), {'id': 'sess_test', 'url': 'https://example.com/checkout'})()
            url, purchase = create_checkout_session(self.user, plan, 'http://example.com/success?session_id={CHECKOUT_SESSION_ID}', 'http://example.com/cancel')
        # Simulate Stripe session object payload
        fake_session = {'data': {'object': {'id': purchase.checkout_session_id, 'payment_intent': 'pi_test'}}}
        handle_checkout_completed(fake_session)
        purchase.refresh_from_db()
        wallet = purchase.user.credit_wallet
        self.assertEqual(purchase.status, Purchase.STATUS_PAID)
        self.assertEqual(purchase.credits_granted, 5)
        self.assertEqual(wallet.balance, 5)

    def test_handle_recalculates_and_grants_when_plan_had_zero(self):
        plan = Plan.objects.create(name='Zero Plan', slug='zero-plan', price_usd=10, credits_on_purchase=0, renewal_interval=Plan.INTERVAL_ONE_OFF, stripe_price_id='price_test2')
        with patch('stripe.Customer.create') as m_cust, patch('stripe.checkout.Session.create') as m_sess:
            m_cust.return_value = type('O', (), {'id': 'cus_test2'})()
            m_sess.return_value = type('O', (), {'id': 'sess_test2', 'url': 'https://example.com/checkout2'})()
            url, purchase = create_checkout_session(self.user, plan, 'http://example.com/success?session_id={CHECKOUT_SESSION_ID}', 'http://example.com/cancel')
        # Now update plan to have credits AFTER purchase was created (simulates admin fix)
        plan.credits_on_purchase = 3
        plan.save()
        fake_session = {'data': {'object': {'id': purchase.checkout_session_id, 'payment_intent': 'pi_test2'}}}
        handle_checkout_completed(fake_session)
        purchase.refresh_from_db()
        wallet = purchase.user.credit_wallet
        self.assertEqual(purchase.status, Purchase.STATUS_PAID)
        self.assertEqual(purchase.credits_granted, 3)
        self.assertEqual(wallet.balance, 3)
