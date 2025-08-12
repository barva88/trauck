from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
from .services.stripe_service import handle_checkout_completed, handle_invoice_paid, handle_payment_failed


stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
stripe.api_version = '2024-06-20'


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    if not endpoint_secret:
        return JsonResponse({'error': 'Webhook secret not configured'}, status=400)
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    event_type = event['type']
    if event_type == 'checkout.session.completed':
        handle_checkout_completed(event)
    elif event_type == 'invoice.paid':
        handle_invoice_paid(event)
    elif event_type == 'invoice.payment_failed':
        handle_payment_failed(event)
    elif event_type in ('customer.subscription.updated','customer.subscription.deleted','charge.refunded'):
        # TODO: extend
        pass
    return HttpResponse(status=200)
