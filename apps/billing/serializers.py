from rest_framework import serializers
from .models import Plan, CreditWallet, ConsumptionEvent, Purchase


class PlanBenefitSerializer(serializers.Serializer):
    label = serializers.CharField()
    order = serializers.IntegerField()

class PlanSerializer(serializers.ModelSerializer):
    benefits = PlanBenefitSerializer(many=True, read_only=True)
    class Meta:
        model = Plan
        fields = ('id','name','slug','is_active','price_usd','currency','credits_on_purchase','renewal_interval','exam_cost_credits','description','benefits','stripe_product_id','stripe_price_id')

    def validate(self, data):
        # If plan has a price > 0, ensure credits_on_purchase is positive
        price = data.get('price_usd', None)
        credits = data.get('credits_on_purchase', None)
        # When updating, fields may be missing from data; fall back to instance
        if self.instance:
            price = price if price is not None else self.instance.price_usd
            credits = credits if credits is not None else self.instance.credits_on_purchase
        if price is not None and float(price) > 0 and (credits is None or int(credits) <= 0):
            raise serializers.ValidationError('Paid plans must have credits_on_purchase > 0')
        return data

class CheckoutSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(required=False)
    pack_id = serializers.IntegerField(required=False)
    mode = serializers.ChoiceField(choices=(('payment','payment'),('subscription','subscription')), required=False)
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()

class PortalSessionSerializer(serializers.Serializer):
    return_url = serializers.URLField(required=False)

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditWallet
        fields = ('balance',)

class ConsumeSerializer(serializers.Serializer):
    service_code = serializers.CharField()
    amount_credits = serializers.IntegerField(min_value=1)
    source = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)

class RefundRequestSerializer(serializers.Serializer):
    purchase_id = serializers.IntegerField()
    reason_text = serializers.CharField(required=False, allow_blank=True)
