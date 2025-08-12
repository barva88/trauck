from django.urls import path
from .views import PlansView, CheckoutView, PortalSessionView, WalletView, ConsumeView, RefundsView, plans_page, wallet_page, portal_open, checkout_success, checkout_cancel, refunds_page
from .webhooks import stripe_webhook

app_name = 'billing'

urlpatterns = [
    path('plans/', PlansView.as_view(), name='plans'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('portal/session/', PortalSessionView.as_view(), name='portal_session'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('consume/', ConsumeView.as_view(), name='consume'),
    path('refunds/', RefundsView.as_view(), name='refunds'),

    # Pages
    path('ui/plans/', plans_page, name='plans_page'),
    path('ui/wallet/', wallet_page, name='wallet_page'),
    path('ui/refunds/', refunds_page, name='refunds_page'),
    path('ui/portal/', portal_open, name='portal_open'),
    path('ui/success/', checkout_success, name='success'),
    path('ui/cancel/', checkout_cancel, name='cancel'),

    # Webhooks
    path('webhooks/stripe/', stripe_webhook, name='stripe_webhook'),
]
