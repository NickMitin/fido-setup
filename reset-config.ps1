# Reset Fidian configuration — regenerate from .env
# Run from project root: .\reset-config.ps1

Set-Location $PSScriptRoot

Write-Host "Stopping containers..." -ForegroundColor Yellow
docker compose down

Write-Host "Removing config volumes (binkd, husky)..." -ForegroundColor Yellow
$volumes = @("fido-setup_binkd_config", "fido-setup_husky_config")
foreach ($v in $volumes) {
    docker volume rm $v 2>$null
    if ($LASTEXITCODE -eq 0) { Write-Host "  Removed $v" } else { Write-Host "  $v not found (ok)" }
}

Write-Host "Starting containers (config will be regenerated from .env)..." -ForegroundColor Green
docker compose up -d

Write-Host "Waiting for container to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "Fixing Husky log permissions..." -ForegroundColor Yellow
docker exec fido-echo bash -c 'mkdir -p /var/log/husky /var/log/binkd && chown -R fido:ftn /var/log/husky /var/log/binkd && chmod -R 775 /var/log/husky /var/log/binkd' 2>$null

Write-Host "Starting TTYd web console (fidian has it disabled by default)..." -ForegroundColor Yellow
docker exec fido-echo supervisorctl start ttyd:ttyd_00 2>$null

Write-Host "`nDone. Configuration has been reset from .env" -ForegroundColor Green
Write-Host "Web console: http://localhost:24580 (user: fido, password: WEB_PASSWORD from .env)" -ForegroundColor Cyan
