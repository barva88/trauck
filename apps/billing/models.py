from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinValueValidator


class Plan(models.Model):
    INTERVAL_MONTHLY = 'MONTHLY'
    INTERVAL_ONE_OFF = 'ONE_OFF'
    INTERVAL_CHOICES = (
        (INTERVAL_MONTHLY, 'Monthly'),
        (INTERVAL_ONE_OFF, 'One-off'),
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=10, default='usd')
    credits_on_purchase = models.PositiveIntegerField(default=0)
    renewal_interval = models.CharField(max_length=16, choices=INTERVAL_CHOICES, default=INTERVAL_ONE_OFF)
    exam_cost_credits = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)

    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PlanBenefit(models.Model):
    plan = models.ForeignKey(Plan, related_name='benefits', on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.plan.name} - {self.label}"


class CreditWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='credit_wallet', on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet({self.user}) balance={self.balance}"

    def debit(self, amount: int, reason: str = '', metadata: dict | None = None):
        from django.db import transaction
        if amount <= 0:
            raise ValueError('amount must be > 0')
        metadata = metadata or {}
        with transaction.atomic():
            w = CreditWallet.objects.select_for_update().get(pk=self.pk)
            if w.balance < amount:
                raise ValueError('Insufficient credits')
            w.balance -= amount
            w.save(update_fields=['balance', 'updated_at'])
            CreditTransaction.objects.create(
                wallet=w,
                type=CreditTransaction.TYPE_DEBIT,
                signed_amount=-amount,
                reason=reason,
                metadata=metadata,
            )
            return w.balance


class CreditTransaction(models.Model):
    TYPE_PURCHASE = 'PURCHASE'
    TYPE_DEBIT = 'DEBIT'
    TYPE_REFUND = 'REFUND'
    TYPE_ADJUST = 'ADJUSTMENT'
    TYPE_RENEWAL = 'SUBSCRIPTION_RENEWAL'
    TYPE_CHOICES = (
        (TYPE_PURCHASE, 'Purchase'),
        (TYPE_DEBIT, 'Debit'),
        (TYPE_REFUND, 'Refund'),
        (TYPE_ADJUST, 'Adjustment'),
        (TYPE_RENEWAL, 'Subscription Renewal'),
    )

    wallet = models.ForeignKey(CreditWallet, related_name='transactions', on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    signed_amount = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', 'id']


class CreditPack(models.Model):
    name = models.CharField(max_length=100)
    credits = models.PositiveIntegerField()
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.credits} cr)"


class ServiceType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    default_cost_credits = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.label


class Purchase(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_PAID = 'PAID'
    STATUS_REFUNDED = 'REFUNDED'
    STATUS_CANCELED = 'CANCELED'
    STATUS_PAST_DUE = 'PAST_DUE'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchases', on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL)
    credit_pack = models.ForeignKey(CreditPack, null=True, blank=True, on_delete=models.SET_NULL)

    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    checkout_session_id = models.CharField(max_length=200, blank=True, null=True)
    subscription_id = models.CharField(max_length=200, blank=True, null=True)
    payment_intent_id = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(max_length=20, default=STATUS_PENDING)
    credits_granted = models.IntegerField(default=0)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)

    guarantee_starts_at = models.DateTimeField(blank=True, null=True)
    guarantee_ends_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def open_guarantee(self):
        start = timezone.now()
        end = start + timezone.timedelta(days=30)
        self.guarantee_starts_at = start
        self.guarantee_ends_at = end
        self.save(update_fields=['guarantee_starts_at', 'guarantee_ends_at', 'updated_at'])
        GuaranteeWindow.objects.update_or_create(purchase=self, defaults={
            'start': start,
            'end': end,
            'status': GuaranteeWindow.STATUS_ACTIVE,
        })

    def __str__(self):
        return f"Purchase #{self.pk} - {self.user} - {self.status}"


class GuaranteeWindow(models.Model):
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_VOID = 'VOID'
    STATUS_REFUNDED = 'REFUNDED'

    purchase = models.OneToOneField(Purchase, related_name='guarantee', on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.CharField(max_length=20, default=STATUS_ACTIVE)


class RefundRequest(models.Model):
    STATUS_REQUESTED = 'REQUESTED'
    STATUS_APPROVED = 'APPROVED'
    STATUS_DECLINED = 'DECLINED'
    STATUS_COMPLETED = 'COMPLETED'

    purchase = models.ForeignKey(Purchase, related_name='refund_requests', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason_text = models.TextField(blank=True)
    refund_amount_usd = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    stripe_refund_id = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, default=STATUS_REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ConsumptionEvent(models.Model):
    wallet = models.ForeignKey(CreditWallet, related_name='consumptions', on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    credits_spent = models.PositiveIntegerField()
    source = models.CharField(max_length=100, blank=True)
    purchase = models.ForeignKey(Purchase, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', 'id']
