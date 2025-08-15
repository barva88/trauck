import pytest
from django.urls import reverse


def test_healthz(client):
    url = reverse("pages:healthz")
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_readiness(client, db):
    url = reverse("pages:readiness")
    resp = client.get(url)
    assert resp.status_code in (200, 503)
    assert "database" in resp.json()
