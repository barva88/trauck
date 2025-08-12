from rest_framework import serializers

class SummaryResponseSerializer(serializers.Serializer):
    revenue = serializers.DictField()
    mrr = serializers.DictField(required=False)
    arr = serializers.DictField(required=False)
    arpu = serializers.DictField(required=False)
    refund_rate = serializers.DictField(required=False)
    active_subscriptions = serializers.DictField(required=False)
    credits = serializers.DictField()
    loads = serializers.DictField(required=False)
    risk = serializers.DictField(required=False)
