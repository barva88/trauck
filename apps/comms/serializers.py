from rest_framework import serializers


class RetellMessageSerializer(serializers.Serializer):
    message_id = serializers.CharField()
    role = serializers.CharField()
    text = serializers.CharField(allow_blank=True)
    timestamp_iso = serializers.CharField(required=False, allow_blank=True)


class RetellNLPSerializer(serializers.Serializer):
    intent = serializers.CharField(required=False, allow_blank=True)
    confidence = serializers.FloatField(required=False)
    entities = serializers.DictField(child=serializers.JSONField(), required=False)
    sentiment = serializers.CharField(required=False, allow_blank=True)


class RetellConversationSerializer(serializers.Serializer):
    conversation_id = serializers.CharField()
    agent_id = serializers.CharField()
    channel = serializers.CharField(required=False, allow_blank=True)
    language = serializers.CharField(required=False, allow_blank=True)


class RetellMetaSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField()
    trace_id = serializers.CharField(required=False, allow_blank=True)


class RetellWebhookSerializer(serializers.Serializer):
    source = serializers.CharField(required=False, allow_blank=True)
    version = serializers.CharField(required=False, allow_blank=True)
    event = serializers.CharField()
    conversation = RetellConversationSerializer()
    message = RetellMessageSerializer(required=False)
    nlp = RetellNLPSerializer(required=False)
    meta = RetellMetaSerializer()

    def validate(self, data):
        msg = data.get('message')
        if msg:
            role = msg.get('role', '')
            if role not in ('user', 'assistant'):
                raise serializers.ValidationError({'message.role': 'role debe ser user|assistant'})
        return data
