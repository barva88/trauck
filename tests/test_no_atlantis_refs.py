from scripts.scan_atlantis import scan


def test_scan_atlantis_empty():
    hits = [h for h in scan() if not h.startswith("themes/django-atlantis-dark/")]
    assert hits == [], f"Atlantis references outside theme: {hits}"
