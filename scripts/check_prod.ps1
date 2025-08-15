# Runs Django deploy checks and tests using prod settings.
param(
  [string]$Python = "python"
)

$env:DJANGO_SETTINGS_MODULE = "config.settings.prod"
Write-Host "[check] Running Django system checks (deploy)..."
$deploy = & $Python manage.py check --deploy
Write-Host $deploy

Write-Host "[check] Running migrations plan..."
$plan = & $Python manage.py showmigrations
Write-Host $plan

Write-Host "[test] Running pytest (uses config.settings.test by default)..."
pytest -q

Write-Host "Done."
