param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$Command,
    [string]$Directory = (Split-Path $PSScriptRoot -Parent)
)
$ErrorActionPreference = 'Stop'
$evidenceDirectory = Join-Path (Split-Path $PSScriptRoot -Parent) 'docs/evidence'
New-Item -ItemType Directory -Force $evidenceDirectory | Out-Null
$started = [DateTimeOffset]::UtcNow
$logPath = Join-Path $evidenceDirectory "$Name.log"
$output = @()
Push-Location -LiteralPath $Directory
try {
    Write-Host "PS $Directory> $Command" -ForegroundColor Cyan
    & (Get-Process -Id $PID).Path -NoProfile -Command $Command 2>&1 | ForEach-Object {
        $line = $_.ToString()
        $output += $line
        Write-Host $line
    }
    $resultCode = $LASTEXITCODE
    if ($null -eq $resultCode) { $resultCode = 0 }
} finally { Pop-Location }
$output | Set-Content -LiteralPath $logPath -Encoding utf8
@{
    name = $Name; command = $Command; directory = $Directory
    started_utc = $started.ToString('o'); finished_utc = [DateTimeOffset]::UtcNow.ToString('o')
    exit_code = $resultCode; output = ($output -join "`n")
} | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $evidenceDirectory "$Name.json") -Encoding utf8
Write-Host "Exit code: $resultCode"
exit $resultCode
