from django.conf import settings


def test_allowed_hosts_contains_domains():
    assert "trauck.com" in settings.ALLOWED_HOSTS
    assert "dashboard.trauck.com" in settings.ALLOWED_HOSTS
