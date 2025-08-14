from pathlib import Path
import pytest


@pytest.mark.xfail(reason="Theme folder pending deletion during cleanup")
def test_atlantis_theme_folder_removed():
    root = Path(__file__).resolve().parents[1]
    assert not (root / "themes" / "django-atlantis-dark").exists()
