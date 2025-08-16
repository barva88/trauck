import importlib
import os
import re
import pytest
from django.core import mail
from django.test import Client, override_settings
from django.template.loader import get_template
from django.urls import reverse, resolve


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_verification_sent_endpoint_renders():
    c = Client()
    url = '/api/auth/registration/account-email-verification-sent/'
    resp = c.get(url)
    assert resp.status_code == 200
    # Ensure the template is used
    assert b'verification' in resp.content.lower()


def test_email_confirm_template_loadable():
    # Loader should find our confirm template
    t = get_template('account/email_confirm.html')
    assert t is not None


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_registration_sends_email_if_endpoint_present(settings):
    # if the dj-rest-auth registration URL is not installed, skip
    try:
        reverse('rest_register')
    except Exception:
        pytest.skip('registration endpoint not present')

    c = Client()
    # Use a unique email
    email = f"tester_{os.getpid()}@example.com"
    data = {
        'email': email,
        'password1': 'Str0ngPass!123',
        'password2': 'Str0ngPass!123',
    }
    # The endpoint name for dj-rest-auth is typically 'rest_register'
    resp = c.post(reverse('rest_register'), data)
    assert resp.status_code in (200, 201)
    # At least one message queued
    assert len(mail.outbox) >= 1
    # Subject and body present
    assert any(re.search(r'confirm|verification', m.subject, re.I) for m in mail.outbox)
