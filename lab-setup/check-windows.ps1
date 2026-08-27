<#
.SYNOPSIS
    Preflight check for a Windows machine before the course.

.DESCRIPTION
    Checks the Windows side (virtualisation, WSL2, the Ubuntu distro, memory
    and disk), then runs the Linux preflight inside Ubuntu so you get one
    answer covering both halves.

    Run it AFTER install-windows.ps1. It changes nothing.

.EXAMPLE
    .\check-windows.ps1
#>
[CmdletBinding()]
param([string]$Distro = 'Ubuntu-24.04')

$rows = @()
$fail = 0

function Add-Row {
    param([string]$Name, [bool]$Pass, [string]$Detail, [switch]$Optional)
    $status = if ($Pass) { 'PASS' } elseif ($Optional) { 'WARN' } else { 'FAIL' }
    if (-not $Pass -and -not $Optional) { $script:fail++ }
    $script:rows += [pscustomobject]@{ STATUS = $status; CHECK = $Name; DETAIL = $Detail }
}

Write-Host ""
Write-Host "Checking Windows host for the course ..." -ForegroundColor White
Write-Host ""

# --- Windows version
$build = [int](Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').CurrentBuildNumber
Add-Row 'Windows build >= 19041' ($build -ge 19041) "build $build"

# --- virtualisation
$hyper = (Get-CimInstance Win32_ComputerSystem).HypervisorPresent
$virt  = (Get-CimInstance Win32_Processor | Select-Object -First 1).VirtualizationFirmwareEnabled
Add-Row 'virtualisation enabled' ($hyper -or $virt) $(if ($hyper) { 'hypervisor present' } else { 'VT-x/AMD-V in firmware' })

# --- RAM and disk on the host
$ramGB  = [math]::Round((Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize / 1MB, 1)
Add-Row 'host RAM >= 8GB' ($ramGB -ge 8) "${ramGB} GB"
$freeGB = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
Add-Row 'free disk >= 25GB' ($freeGB -ge 25) "${freeGB} GB free on C:"

# --- WSL
$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue
Add-Row 'WSL installed' ($null -ne $wsl) $(if ($wsl) { 'wsl.exe found' } else { 'run install-windows.ps1' })

if ($wsl) {
    $distros = (wsl.exe --list --quiet) -replace "`0", "" | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    Add-Row "$Distro installed" ($distros -contains $Distro) ($distros -join ', ')

    $verLine = ((wsl.exe --list --verbose) -replace "`0", "" | Select-String $Distro | Select-Object -First 1)
    $verText = if ($verLine) { ($verLine.ToString() -replace '\s+', ' ').Trim() } else { 'not listed' }
    Add-Row 'running WSL version 2' ($verText -match '\s2$') $verText

    if ($distros -contains $Distro) {
        $sysd = (wsl.exe -d $Distro -- bash -lc "grep -qs 'systemd=true' /etc/wsl.conf && echo yes || echo no").Trim()
        Add-Row 'systemd enabled in Ubuntu' ($sysd -eq 'yes') $(if ($sysd -eq 'yes') { '/etc/wsl.conf' } else { 'Docker will not start without it' })

        $wslMem = (wsl.exe -d $Distro -- bash -lc "free -g | awk '/^Mem:/{print `$2}'").Trim()
        Add-Row 'RAM inside Ubuntu >= 6GB' ([int]$wslMem -ge 6) "${wslMem} GB (set in %UserProfile%\.wslconfig)"

        $repo = (wsl.exe -d $Distro -- bash -lc "[ -d ~/devops-course/lab-setup ] && echo yes || echo no").Trim()
        Add-Row 'course repo cloned' ($repo -eq 'yes') '~/devops-course'
    }
}

$rows | Format-Table -AutoSize

if ($fail -gt 0) {
    Write-Host "RESULT: $fail Windows-side check(s) FAILED. Fix these, then re-run." -ForegroundColor Red
    Write-Host "Most problems are fixed by running install-windows.ps1 as administrator." -ForegroundColor Yellow
    exit 1
}

Write-Host "RESULT: the Windows side is ready." -ForegroundColor Green
Write-Host ""
Write-Host "Now checking the Linux side inside ${Distro} ..." -ForegroundColor White
Write-Host ""
wsl.exe -d $Distro -- bash -lc "cd ~/devops-course && ./lab-setup/check-environment.sh"
exit $LASTEXITCODE
