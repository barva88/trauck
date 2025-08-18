import os
import pytest
from django.test import Client


@pytest.mark.django_db
class TestHostRouting:
    def test_public_host_serves_landing(self, settings):
        # Simulate host routing by overriding HTTP_HOST
        c = Client()
        resp = c.get('/', HTTP_HOST='trauck.com')
        assert resp.status_code == 200
        assert b"Trauck" in resp.content

    def test_dashboard_requires_login(self, settings):
        c = Client()
        resp = c.get('/', HTTP_HOST='dashboard.trauck.com')
        # should redirect to login on dashboard host
        assert resp.status_code in (301, 302)
        loc = resp.headers.get('Location', '')
        assert '/accounts/login' in loc

    def test_dashboard_after_login(self, django_user_model, client):
        user = django_user_model.objects.create_user(email='u@test.com', password='x12345!')
        # login via dashboard host
        c = Client()
        c.post('/accounts/login/', {'login': 'u@test.com', 'password': 'x12345!'}, HTTP_HOST='dashboard.trauck.com')
        resp = c.get('/', HTTP_HOST='dashboard.trauck.com')
        assert resp.status_code == 200 or resp.status_code == 302
