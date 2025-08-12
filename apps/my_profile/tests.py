from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile


class ProfileModelTests(TestCase):
    def test_profile_str(self):
        User = get_user_model()
        u = User.objects.create_user(username='john', password='pass')
        p = Profile.objects.filter(user=u).first() or Profile.objects.create(user=u)
        self.assertIn('john', str(p))
