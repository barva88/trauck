import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"atlantis|django-atlantis-dark|admin_atlantis", re.IGNORECASE)

def test_no_atlantis_references_outside_theme():
    forbidden = []
    for dirpath, _, filenames in os.walk(ROOT):
        rel_dir = Path(dirpath).relative_to(ROOT)
        # allow the themes/django-atlantis-dark tree to exist temporarily
        if str(rel_dir).startswith("themes/django-atlantis-dark"):
            continue
        if any(p in dirpath for p in (os.sep+".venv"+os.sep, os.sep+"node_modules"+os.sep)):
            continue
        for fn in filenames:
            path = Path(dirpath) / fn
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if PATTERN.search(text):
                forbidden.append(str(path.relative_to(ROOT)))
    assert not forbidden, f"Atlantis references found: {forbidden}"
