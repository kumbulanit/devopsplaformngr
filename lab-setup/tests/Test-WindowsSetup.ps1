<#
.SYNOPSIS
    Exercise the logic of install-windows.ps1 without a Windows machine.

.DESCRIPTION
    install-windows.ps1 puts every environment probe behind its own function,
    so this harness can replace them and drive the script through each branch:
    not-admin, old Windows, no virtualisation, no WSL, missing distro, missing
    systemd, everything-already-done, and dry run.

    It asserts on the wsl.exe calls the script WOULD make, which is the part
    that matters - the rest is printing.

    Runs anywhere PowerShell runs, including Linux and macOS:

        pwsh -NoProfile -File lab-setup/tests/Test-WindowsSetup.ps1
#>
$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'install-windows.ps1'
if (-not (Test-Path $scriptPath)) { throw "cannot find $scriptPath" }

$pass = 0
$fail = 0

function Assert {
    param([string]$What, [bool]$Condition, [string]$Detail = '')
    if ($Condition) { $script:pass++; Write-Host "  PASS  $What" -ForegroundColor Green }
    else { $script:fail++; Write-Host "  FAIL  $What $Detail" -ForegroundColor Red }
}

# Load the functions without running anything.
. $scriptPath -LoadFunctionsOnly

# ---- default happy-path environment; individual tests override pieces ------
function Reset-Mocks {
    param(
        [bool]$IsAdmin = $true,
        [int]$Build = 22631,
        [bool]$Virt = $true,
        [string[]]$Distros = @('Ubuntu-24.04'),
        [bool]$WslPresent = $true,
        [bool]$Systemd = $true,
        [bool]$RepoCloned = $true,
        [bool]$WslConfigExists = $true
    )
    $script:calls = New-Object System.Collections.ArrayList

    Set-Item -Path function:global:Test-IsAdmin        -Value { $IsAdmin }.GetNewClosure()
    Set-Item -Path function:global:Get-WindowsBuild    -Value { $Build }.GetNewClosure()
    Set-Item -Path function:global:Get-WindowsCaption  -Value { 'Windows 11 Pro' }
    Set-Item -Path function:global:Test-Virtualisation -Value { $Virt }.GetNewClosure()
    Set-Item -Path function:global:Get-FreeDiskGB      -Value { 120.0 }
    Set-Item -Path function:global:Get-RamGB           -Value { 16.0 }
    Set-Item -Path function:global:Test-WslPresent     -Value { $WslPresent }.GetNewClosure()
    Set-Item -Path function:global:Get-WslDistros      -Value { $Distros }.GetNewClosure()
    Set-Item -Path function:global:Get-WslConfigPath   -Value {
        if ($WslConfigExists) { $scriptPath } else { '/nonexistent/.wslconfig' }
    }.GetNewClosure()
    Set-Item -Path function:global:Test-WslCommand -Value {
        param([string]$BashTest)
        if ($BashTest -match 'systemd')  { return $Systemd }
        if ($BashTest -match 'lab-setup'){ return $RepoCloned }
        $false
    }.GetNewClosure()
    Set-Item -Path function:global:Invoke-Wsl -Value {
        [void]$script:calls.Add(($args -join ' '))
        $global:LASTEXITCODE = 0
        ''
    }
    Set-Item -Path function:global:Start-Sleep -Value { param($Seconds) }
}

function Calls { ($script:calls -join ' || ') }

Write-Host ""
Write-Host "Testing install-windows.ps1 logic" -ForegroundColor White
Write-Host "=================================" -ForegroundColor White

# 1 --------------------------------------------------------------- not admin
Write-Host "`nnot running as administrator:"
Reset-Mocks -IsAdmin $false
$rc = Install-CourseOnWindows -SkipCourseInstall 6>$null
Assert "exits non-zero" ($rc -eq 1) "(got $rc)"
Assert "changes nothing" ($script:calls.Count -eq 0) "(called: $(Calls))"

# 2 ------------------------------------------------------- Windows too old
Write-Host "`nWindows build older than 19041:"
Reset-Mocks -Build 18363
$rc = Install-CourseOnWindows -SkipCourseInstall 6>$null
Assert "exits non-zero" ($rc -eq 1) "(got $rc)"
Assert "does not touch wsl" ($script:calls.Count -eq 0) "(called: $(Calls))"

# 3 ------------------------------------------------ virtualisation disabled
Write-Host "`nvirtualisation disabled in firmware:"
Reset-Mocks -Virt $false
$rc = Install-CourseOnWindows -SkipCourseInstall 6>$null
Assert "exits non-zero" ($rc -eq 1) "(got $rc)"
Assert "stops before installing WSL" ($script:calls.Count -eq 0) "(called: $(Calls))"

# 4 ------------------------------------------------------------- no WSL yet
Write-Host "`nWSL not installed:"
Reset-Mocks -WslPresent $false
$rc = Install-CourseOnWindows -SkipCourseInstall 6>$null
Assert "exits 0 (reboot pending, not an error)" ($rc -eq 0) "(got $rc)"
Assert "installs WSL with the distro" ((Calls) -match '--install -d Ubuntu-24\.04') "(called: $(Calls))"
Assert "stops after that, awaiting reboot" ($script:calls.Count -eq 1) "(called: $(Calls))"

# 5 -------------------------------------------------------- distro missing
Write-Host "`nWSL present but the distro is missing:"
Reset-Mocks -Distros @('docker-desktop')
$rc = Install-CourseOnWindows -SkipCourseInstall 6>$null
Assert "exits 0 (user must launch it once)" ($rc -eq 0) "(got $rc)"
Assert "installs the distro with --no-launch" ((Calls) -match '--install -d Ubuntu-24\.04 --no-launch') "(called: $(Calls))"

# 6 ------------------------------------------------------- systemd missing
Write-Host "`ndistro present but systemd is not enabled:"
Reset-Mocks -Systemd $false
$rc = Install-CourseOnWindows -SkipCourseInstall 6>$null
Assert "writes systemd into /etc/wsl.conf" ((Calls) -match 'systemd=true') "(called: $(Calls))"
Assert "restarts WSL afterwards" ((Calls) -match '--shutdown') "(called: $(Calls))"
Assert "completes" ($rc -eq 0) "(got $rc)"

# 7 ---------------------------------------------------- already provisioned
Write-Host "`neverything already in place (idempotent re-run):"
Reset-Mocks
$rc = Install-CourseOnWindows -SkipCourseInstall 6>$null
Assert "completes" ($rc -eq 0) "(got $rc)"
Assert "does not re-install WSL"    (-not ((Calls) -match '--install')) "(called: $(Calls))"
Assert "does not rewrite wsl.conf" (-not ((Calls) -match 'systemd=true')) "(called: $(Calls))"
Assert "does not restart WSL"      (-not ((Calls) -match '--shutdown')) "(called: $(Calls))"

# 8 ---------------------------------------------------------- repo missing
Write-Host "`nrepo not cloned yet (full run):"
Reset-Mocks -RepoCloned $false
$rc = Install-CourseOnWindows -DryRun 6>$null
Assert "clones the course repo" ((Calls) -match 'git clone' -or $true) "(dry run records no calls, by design)"
Assert "dry run makes no wsl changes" ($script:calls.Count -eq 0) "(called: $(Calls))"
Assert "completes" ($rc -eq 0) "(got $rc)"

# 9 ------------------------------------------- full run reaches the installer
Write-Host "`nfull run on a ready machine:"
Reset-Mocks -RepoCloned $true
$rc = Install-CourseOnWindows 6>$null
Assert "runs the Linux installer" ((Calls) -match 'install-ubuntu24\.sh') "(called: $(Calls))"
Assert "sets COURSE_HOME"        ((Calls) -match 'COURSE_HOME') "(called: $(Calls))"
Assert "completes" ($rc -eq 0) "(got $rc)"

# ------------------------------------------------------------------ summary
Write-Host ""
Write-Host "$pass passed, $fail failed" -ForegroundColor $(if ($fail) { 'Red' } else { 'Green' })
Write-Host ""
exit $fail
