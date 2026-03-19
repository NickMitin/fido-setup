# Verify env vars reach the container and BinkD config
Write-Host "=== Container environment (UPLINK_*, YOUR_*) ===" -ForegroundColor Cyan
docker exec fido-echo env 2>$null | Select-String -Pattern "UPLINK|YOUR_|LINK_|SESSION_PASSWORD"

Write-Host "`n=== /home/fido/.fidoconfig ===" -ForegroundColor Cyan
docker exec fido-echo cat /home/fido/.fidoconfig 2>$null

Write-Host "`n=== BinkD link config (binkd.inc) ===" -ForegroundColor Cyan
docker exec fido-echo cat /etc/binkd/binkd.inc 2>$null
