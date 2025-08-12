from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib import messages

from .serializers import PlanSerializer, CheckoutSerializer, PortalSessionSerializer, WalletSerializer, ConsumeSerializer, RefundRequestSerializer
from .selectors import active_plans, get_wallet_for_user
from .services.stripe_service import create_checkout_session, create_billing_portal_session, debit_credits, current_balance, request_refund, complete_checkout_by_session_id
from .models import Plan, CreditPack, Purchase
from .forms import RefundRequestForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie


class PlansView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        plans = active_plans()
        return Response(PlanSerializer(plans, many=True).data)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        s = CheckoutSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        plan_id = s.validated_data.get('plan_id')
        pack_id = s.validated_data.get('pack_id')
        mode = s.validated_data.get('mode') or 'payment'
        success_url = s.validated_data['success_url']
        cancel_url = s.validated_data['cancel_url']
        obj = None
        if plan_id:
            obj = Plan.objects.get(pk=plan_id)
            if obj.renewal_interval == Plan.INTERVAL_MONTHLY:
                mode = 'subscription'
        elif pack_id:
            obj = CreditPack.objects.get(pk=pack_id)
            mode = 'payment'
        else:
            return Response({'error': 'Provide plan_id or pack_id'}, status=400)
        try:
            url, purchase = create_checkout_session(request.user, obj, success_url, cancel_url, mode=mode)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'Stripe error: ' + str(e)}, status=400)
        return Response({'url': url, 'purchase_id': purchase.id})


class PortalSessionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        s = PortalSessionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        url = create_billing_portal_session(request.user, s.validated_data.get('return_url'))
        return Response({'url': url})


class WalletView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        wallet = get_wallet_for_user(request.user)
        return Response(WalletSerializer(wallet).data)


class ConsumeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        s = ConsumeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        debit_credits(request.user, s.validated_data['service_code'], s.validated_data['amount_credits'], s.validated_data.get('metadata') or {})
        return Response({'ok': True, 'balance': current_balance(request.user)})


class RefundsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = Purchase.objects.filter(user=request.user, status=Purchase.STATUS_PAID)
        return Response({'eligible_purchases': [p.id for p in qs]})

    def post(self, request):
        s = RefundRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        purchase = Purchase.objects.get(pk=s.validated_data['purchase_id'], user=request.user)
        try:
            amount = request_refund(request.user, purchase)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        return Response({'ok': True, 'refund_amount': amount})


# Simple pages using existing layout
from config.menu_config import MENU_ITEMS

@ensure_csrf_cookie
def plans_page(request):
    context = {
        'menu_items': MENU_ITEMS,
        'segment': 'billing',
        'plans': active_plans(),
        'success_url': request.build_absolute_uri(reverse('billing:success')),
        'cancel_url': request.build_absolute_uri(reverse('billing:cancel')),
    }
    return render(request, 'billing/plans.html', context)


@ensure_csrf_cookie
def wallet_page(request):
    from .models import CreditTransaction
    wallet = None
    transactions = []
    if request.user.is_authenticated:
        wallet = get_wallet_for_user(request.user)
        transactions = wallet.transactions.all()[:50]
    context = {
        'menu_items': MENU_ITEMS,
        'segment': 'billing',
        'wallet': wallet,
        'transactions': transactions,
    }
    return render(request, 'billing/wallet.html', context)


@login_required
def portal_open(request):
    try:
        url = create_billing_portal_session(request.user, getattr(settings, 'STRIPE_PORTAL_RETURN_URL', '/'))
        return redirect(url)
    except Exception as e:
        messages.error(request, f"No se pudo abrir el portal de facturación: {e}")
        return redirect('billing:wallet_page')


def checkout_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            complete_checkout_by_session_id(session_id)
        except Exception:
            pass
    context = {
        'menu_items': MENU_ITEMS,
        'segment': 'billing',
    }
    return render(request, 'billing/success.html', context)


def checkout_cancel(request):
    context = {
        'menu_items': MENU_ITEMS,
        'segment': 'billing',
    }
    return render(request, 'billing/cancel.html', context)


@login_required
def refunds_page(request):
    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            purchase = Purchase.objects.filter(id=form.cleaned_data['purchase_id'], user=request.user).first()
            if not purchase:
                return render(request, 'billing/refunds.html', {
                    'menu_items': MENU_ITEMS,
                    'segment': 'billing',
                    'error': 'Compra no encontrada',
                    'eligible': Purchase.objects.filter(user=request.user, status=Purchase.STATUS_PAID),
                    'form': form,
                })
            try:
                amount = request_refund(request.user, purchase)
                return render(request, 'billing/refunds.html', {
                    'menu_items': MENU_ITEMS,
                    'segment': 'billing',
                    'success': f'Reembolso procesado por ${amount}',
                    'eligible': Purchase.objects.filter(user=request.user, status=Purchase.STATUS_PAID),
                    'form': RefundRequestForm(),
                })
            except ValueError as e:
                return render(request, 'billing/refunds.html', {
                    'menu_items': MENU_ITEMS,
                    'segment': 'billing',
                    'error': str(e),
                    'eligible': Purchase.objects.filter(user=request.user, status=Purchase.STATUS_PAID),
                    'form': form,
                })
    else:
        form = RefundRequestForm()
    context = {
        'menu_items': MENU_ITEMS,
        'segment': 'billing',
        'eligible': Purchase.objects.filter(user=request.user, status=Purchase.STATUS_PAID),
        'form': form,
    }
    return render(request, 'billing/refunds.html', context)
