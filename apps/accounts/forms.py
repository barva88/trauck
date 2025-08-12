from allauth.account.forms import SignupForm
from django import forms

class CustomSignupForm(SignupForm):
    full_name = forms.CharField(max_length=150, required=False, label='Nombre')
    phone = forms.CharField(max_length=32, required=False, label='Teléfono')

    def save(self, request):
        user = super().save(request)
        # Crear o actualizar perfil
        from apps.my_profile.models import Profile
        Profile.objects.get_or_create(user=user)
        return user
