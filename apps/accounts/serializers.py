from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.my_profile.models import Profile

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'avatar', 'bio', 'external_id', 'stripe_customer_id']
        read_only_fields = ['external_id', 'stripe_customer_id']

class MeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        prof, _ = Profile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(prof, attr, value)
        prof.save()
        return instance
