# Download FidoNet nodelist from wfido.ru (Fidian's default source is down)
# Run: .\fetch-nodelist.ps1
# Requires: Docker container fido-echo running

$dayOfYear = (Get-Date).DayOfYear.ToString("000")
$year = (Get-Date).Year

Write-Host "Fetching nodelist.$dayOfYear from wfido.ru (year $year)..." -ForegroundColor Yellow
docker exec fido-echo wget -q -O "/var/spool/ftn/nodelist/NODELIST.$dayOfYear" "ftp://wfido.ru/nodehist/$year/nodelist.$dayOfYear"

if ($LASTEXITCODE -eq 0) {
    docker exec fido-echo chown ftn:ftn "/var/spool/ftn/nodelist/NODELIST.$dayOfYear"
    docker exec fido-echo chmod 660 "/var/spool/ftn/nodelist/NODELIST.$dayOfYear"
    Write-Host "Done. Nodelist saved to /var/spool/ftn/nodelist/NODELIST.$dayOfYear" -ForegroundColor Green
} else {
    Write-Host "Download failed. Try manually: ftp://wfido.ru/nodehist/$year/nodelist.$dayOfYear" -ForegroundColor Red
    exit 1
}
