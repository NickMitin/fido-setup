# Fix Husky log permissions — run after container start
# hpt and htick need write access to /var/log/husky

Set-Location $PSScriptRoot

Write-Host "Fixing Husky log permissions in container..." -ForegroundColor Cyan

docker exec fido-echo bash -c 'mkdir -p /var/log/husky /var/log/binkd'
docker exec fido-echo bash -c 'chown -R fido:ftn /var/log/husky /var/log/binkd'
docker exec fido-echo bash -c 'chmod -R 775 /var/log/husky /var/log/binkd'
docker exec fido-echo bash -c 'chown -R fido:ftn /var/spool/ftn'
docker exec fido-echo bash -c 'chmod -R 775 /var/spool/ftn'

docker exec fido-echo supervisorctl restart binkd:binkd_00 2>$null

Write-Host "`nDone. Permissions fixed — try poll.sh and toss.sh again." -ForegroundColor Green
