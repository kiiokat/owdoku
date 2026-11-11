# get-hero-portraits.ps1
# Downloads every hero portrait from https://overwatch.blizzard.com/en-us/heroes/
# into a "hero-portraits" folder next to this script, plus a heroes.json list.
# Images are saved exactly as Blizzard serves them (no editing).
#
# Run from PowerShell in the folder where you saved this file:
#   powershell -ExecutionPolicy Bypass -File .\get-hero-portraits.ps1

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$pageUrl = 'https://overwatch.blizzard.com/en-us/heroes/'
$ua      = 'OWdoku fan project - one-time hero portrait download'
$base    = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
# Inside the OWdoku repository, save straight into the game's heroes folder
$repoHeroes = Join-Path $base '..\heroes'
$outDir  = if (Test-Path $repoHeroes) { (Resolve-Path $repoHeroes).Path } else { Join-Path $base 'hero-portraits' }
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Host "Reading $pageUrl ..."
$html = (Invoke-WebRequest -Uri $pageUrl -UseBasicParsing -UserAgent $ua).Content

# Each hero card looks like:
#   <a class="hero-card" ... data-role="damage" ... id="tracer"> ... <blz-image class="heroCardPortrait" ... src="https://...png">
$pattern = '<a class="hero-card"[^>]*?data-role="(?<role>[^"]+)"[^>]*?id="(?<id>[^"]+)"[\s\S]*?class="heroCardPortrait"[^>]*?src="(?<src>[^"]+)"'
$found = [regex]::Matches($html, $pattern)

if ($found.Count -eq 0) {
    Write-Host "No hero cards found - Blizzard may have changed the page layout." -ForegroundColor Red
    exit 1
}
Write-Host "Found $($found.Count) heroes. Downloading..."

$manifest = @()
$ok = 0; $failed = @()
foreach ($m in $found) {
    $id   = $m.Groups['id'].Value
    $role = $m.Groups['role'].Value
    $src  = $m.Groups['src'].Value
    $file = Join-Path $outDir "$id.png"
    try {
        Invoke-WebRequest -Uri $src -OutFile $file -UseBasicParsing -UserAgent $ua
        $ok++
        Write-Host ("  {0,-15} {1}" -f $id, $role)
    } catch {
        $failed += $id
        Write-Host "  $id FAILED: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    $manifest += [pscustomobject]@{ id = $id; role = $role; file = "$id.png"; source = $src }
    Start-Sleep -Milliseconds 250   # be polite to Blizzard's servers
}

$manifest | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $outDir 'heroes.json')

Write-Host ""
Write-Host "Done: $ok of $($found.Count) saved to $outDir" -ForegroundColor Green
if ($failed.Count) { Write-Host "Failed: $($failed -join ', ') - just run the script again." -ForegroundColor Yellow }
