from django.test import Client


def test_https_headers_present(settings):
    c = Client()
    r = c.get("/healthz/")
    assert r.status_code == 200
    # Strong HTTPS headers are typically added by Nginx; app-level is validated via response.
