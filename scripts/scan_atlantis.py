import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"atlantis|django-atlantis-dark|admin_atlantis", re.IGNORECASE)

ALLOWLIST = {
    # Paths that may legitimately contain the word Atlantis (images/docs under theme folder until deletion)
}

def scan():
    hits = []
    for dirpath, _, filenames in os.walk(ROOT):
        # Skip virtualenvs and node modules
        if any(p in dirpath for p in (os.sep+".venv"+os.sep, os.sep+"node_modules"+os.sep)):
            continue
        for fn in filenames:
            path = Path(dirpath) / fn
            rel = path.relative_to(ROOT)
            if rel.as_posix() in ALLOWLIST:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if PATTERN.search(text):
                hits.append(str(rel))
    return sorted(set(hits))

if __name__ == "__main__":
    for f in scan():
        print(f)
