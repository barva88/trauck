import os
import re
import pytest
from django.core import mail
from django.urls import reverse
from django.test import Client, override_settings


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_signup_redirects_and_email_sent(settings):
    """
    Using dj-rest-auth registration, ensure we get a 200/201 and an email with a confirm link,
    and that visiting login/signup pages on dashboard host is allowed for anonymous.
    """
    # If registration endpoint isn't installed, skip
    try:
        register_url = reverse('rest_register')
    except Exception:
        pytest.skip('registration endpoint not present')

    email = f"signup_{os.getpid()}@example.com"
    c = Client()
    # Registration occurs on dashboard host API
    resp = c.post(register_url, {
        'email': email,
        'password1': 'Str0ngPass!123',
        'password2': 'Str0ngPass!123',
    }, HTTP_HOST='dashboard.trauck.com')
    assert resp.status_code in (200, 201)
    assert len(mail.outbox) >= 1
    # Confirm email contains a confirmation URL
    body = '\n'.join(m.body for m in mail.outbox)
    assert re.search(r'/accounts/confirm-email/\S+', body)

    # Anonymous can access login/signup on dashboard host (no forced redirect)
    resp_login = c.get('/accounts/login/', HTTP_HOST='dashboard.trauck.com')
    assert resp_login.status_code == 200
    resp_signup = c.get('/accounts/signup/', HTTP_HOST='dashboard.trauck.com')
    assert resp_signup.status_code == 200


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_email_confirm_then_redirects_to_dashboard(settings):
    """Simulate allauth email confirmation flow and ensure redirect goes to dashboard host index."""
    # Create a user via registration to generate a confirmation
    try:
        register_url = reverse('rest_register')
    except Exception:
        pytest.skip('registration endpoint not present')

    email = f"confirm_{os.getpid()}@example.com"
    c = Client()
    resp = c.post(register_url, {
        'email': email,
        'password1': 'Str0ngPass!123',
        'password2': 'Str0ngPass!123',
    }, HTTP_HOST='dashboard.trauck.com')
    assert resp.status_code in (200, 201)
    assert len(mail.outbox) >= 1

    # Extract confirmation URL from email
    body = '\n'.join(m.body for m in mail.outbox)
    m = re.search(r'(https?://[^\s]+/accounts/confirm-email/[^\s/]+)/?\s', body)
    if not m:
        # Fallback: relative path
        m = re.search(r'(/accounts/confirm-email/[^\s/]+)/?\s', body)
        base = 'http://dashboard.trauck.com'
        confirm_url = base + m.group(1) if m else None
    else:
        confirm_url = m.group(1)
    assert confirm_url, f"No confirmation URL found in email body: {body}"

    # Visit the confirmation URL; expect redirect to dashboard index
    # Use follow=False to inspect the Location header
    resp2 = c.get(confirm_url, follow=False)
    assert resp2.status_code in (301, 302)
    loc = resp2.headers.get('Location', '')
    assert 'dashboard.trauck.com' in loc or loc.startswith('/')


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_allauth_signup_redirects_to_verification_sent(settings):
    """Posting to allauth form signup should redirect to verification-sent page on dashboard host."""
    c = Client()
    email = f"form_{os.getpid()}@example.com"
    data = {
        'email': email,
        'password1': 'Str0ngPass!123',
        'password2': 'Str0ngPass!123',
    }
    resp = c.post('/accounts/signup/', data, HTTP_HOST='dashboard.trauck.com', follow=False)
    assert resp.status_code in (302, 303)
    loc = resp.headers.get('Location', '')
    # allauth default name: account_email_verification_sent
    try:
        expected = reverse('account_email_verification_sent')
        assert expected in loc
    except Exception:
        assert 'verification' in loc


@pytest.mark.django_db
def test_forced_login_url_host_redirect(settings):
    """Anonymous access to dashboard index should redirect to settings.LOGIN_URL on dashboard host."""
    c = Client()
    resp = c.get('/', HTTP_HOST='dashboard.trauck.com', follow=False)
    assert resp.status_code in (301, 302)
    loc = resp.headers.get('Location', '')
    # LOGIN_URL may be absolute; assert it targets dashboard host
    assert 'dashboard.trauck.com' in loc or loc.startswith('/accounts/login')
