<#
.SYNOPSIS
    Prepare a Windows machine for the DevOps & Platform Engineering course.

.DESCRIPTION
    The course runs on Ubuntu 24.04. On Windows the supported route is WSL2:
    a real Ubuntu 24.04 kernel inside Windows, where every lab command works
    unchanged and Ansible (Lab Day 1 Part F) can run at all.

    This script:
      1. checks Windows version, virtualisation and disk
      2. installs WSL2 and the Ubuntu-24.04 distro if missing
      3. writes %UserProfile%\.wslconfig so the VM gets enough memory
      4. enables systemd inside the distro (Docker needs it)
      5. clones the course repo inside Ubuntu and runs the Linux installer

    Docker Desktop is NOT required. Docker Engine is installed inside Ubuntu
    by the course installer, which avoids Docker Desktop licensing entirely -
    relevant for larger organisations.

    Safe to re-run: every step checks whether it is already done.

.PARAMETER DryRun
    Print what would happen without changing anything.

.PARAMETER SkipCourseInstall
    Set up WSL2 + Ubuntu only; do not clone the repo or run the Linux installer.

.EXAMPLE
    # In an ADMINISTRATOR PowerShell window:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
    .\install-windows.ps1
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$SkipCourseInstall
)

$ErrorActionPreference = 'Stop'
$Distro   = 'Ubuntu-24.04'
$RepoUrl  = 'https://github.com/kumbulanit/devopsplaformngr.git'
$RepoDir  = 'devops-course'

function Write-Step  { param($m) Write-Host "[labsetup] $m" -ForegroundColor Cyan }
function Write-Ok    { param($m) Write-Host "[labsetup] $m" -ForegroundColor Green }
function Write-Warn2 { param($m) Write-Host "[labsetup] $m" -ForegroundColor Yellow }
function Write-Err   { param($m) Write-Host "[labsetup] $m" -ForegroundColor Red }

function Invoke-Step {
    param([string]$Description, [scriptblock]$Action)
    Write-Step $Description
    if ($DryRun) { Write-Host "           (dry run - skipped)" -ForegroundColor DarkGray; return }
    & $Action
}

# --------------------------------------------------------------- 0. checks
Write-Host ""
Write-Host "DevOps & Platform Engineering - Windows setup" -ForegroundColor White
Write-Host "=============================================" -ForegroundColor White
Write-Host ""

if ($DryRun) { Write-Warn2 "DRY RUN: nothing will be changed." }

$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Err "This script must run in an ADMINISTRATOR PowerShell window."
    Write-Err "Right-click PowerShell -> 'Run as administrator', then run it again."
    exit 1
}

$os = Get-CimInstance Win32_OperatingSystem
$build = [int](Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').CurrentBuildNumber
Write-Step "Windows: $($os.Caption) (build $build)"
if ($build -lt 19041) {
    Write-Err "WSL2 needs Windows 10 build 19041 (version 2004) or newer. Update Windows first."
    exit 1
}

$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
if (-not $cpu.VirtualizationFirmwareEnabled -and -not (Get-CimInstance Win32_ComputerSystem).HypervisorPresent) {
    Write-Err "Hardware virtualisation is disabled. Enable Intel VT-x / AMD-V in the BIOS/UEFI."
    Write-Err "On a corporate laptop this may need your IT team."
    exit 1
}
Write-Ok "Virtualisation is available"

$freeGB = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
Write-Step "Free space on C: ${freeGB} GB"
if ($freeGB -lt 25) {
    Write-Warn2 "Less than 25 GB free. The course needs ~20 GB of images; free some space."
}

$ramGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
Write-Step "Physical RAM: ${ramGB} GB"
if ($ramGB -lt 8) {
    Write-Warn2 "8 GB or more is recommended (WSL2 will be given 6 GB, leaving little for Windows)."
}

# ------------------------------------------------------------------ 1. WSL
$wslInstalled = $null -ne (Get-Command wsl.exe -ErrorAction SilentlyContinue)

if (-not $wslInstalled) {
    Invoke-Step "Installing WSL2 and $Distro (this reboots-pending on some builds)" {
        wsl.exe --install -d $Distro
    }
    Write-Warn2 ""
    Write-Warn2 "WSL was just installed. REBOOT WINDOWS NOW, then:"
    Write-Warn2 "  1. open the Ubuntu app from the Start menu and create your Linux username/password"
    Write-Warn2 "  2. run this script again to finish the setup"
    Write-Warn2 ""
    exit 0
}

Write-Ok "WSL is present"
Invoke-Step "Ensuring WSL defaults to version 2" { wsl.exe --set-default-version 2 | Out-Null }

$distros = (wsl.exe --list --quiet) -replace "`0", "" | ForEach-Object { $_.Trim() } | Where-Object { $_ }
if ($distros -contains $Distro) {
    Write-Ok "$Distro is already installed"
} else {
    Invoke-Step "Installing the $Distro distro" { wsl.exe --install -d $Distro --no-launch }
    Write-Warn2 ""
    Write-Warn2 "Now open the '$Distro' app from the Start menu once, create your Linux"
    Write-Warn2 "username and password, then re-run this script."
    Write-Warn2 ""
    exit 0
}

Invoke-Step "Making $Distro the default distro" { wsl.exe --set-default $Distro | Out-Null }

# ------------------------------------------------------- 2. .wslconfig (RAM)
$wslConfig = Join-Path $env:USERPROFILE '.wslconfig'
if (Test-Path $wslConfig) {
    Write-Ok ".wslconfig already exists (leaving it alone): $wslConfig"
} else {
    Invoke-Step "Writing $wslConfig so the labs get enough memory" {
        @"
# Resources for the DevOps & Platform Engineering course.
# kind plus the observability stack need roughly 6 GB.
[wsl2]
memory=6GB
processors=4
swap=2GB
"@ | Set-Content -Path $wslConfig -Encoding ASCII
    }
}

# ------------------------------------------------- 3. systemd inside Ubuntu
$hasSystemd = (wsl.exe -d $Distro -- bash -lc "grep -qs 'systemd=true' /etc/wsl.conf && echo yes || echo no").Trim()
if ($hasSystemd -eq 'yes') {
    Write-Ok "systemd is already enabled inside $Distro"
} else {
    Invoke-Step "Enabling systemd inside $Distro (Docker needs it)" {
        wsl.exe -d $Distro -- bash -lc "printf '[boot]\nsystemd=true\n' | sudo tee /etc/wsl.conf >/dev/null"
    }
    Invoke-Step "Restarting WSL so systemd starts" { wsl.exe --shutdown }
    Start-Sleep -Seconds 8
}

# --------------------------------------------- 4. the course inside Ubuntu
if ($SkipCourseInstall) {
    Write-Ok "Skipping the course install (-SkipCourseInstall)"
} else {
    Invoke-Step "Installing git inside $Distro" {
        wsl.exe -d $Distro -- bash -lc "command -v git >/dev/null || (sudo apt-get update -qq && sudo apt-get install -y -qq git)"
    }

    $cloned = (wsl.exe -d $Distro -- bash -lc "[ -d ~/$RepoDir/lab-setup ] && echo yes || echo no").Trim()
    if ($cloned -eq 'yes') {
        Write-Ok "Course repository already cloned at ~/$RepoDir"
    } else {
        Invoke-Step "Cloning the course repository into ~/$RepoDir" {
            wsl.exe -d $Distro -- bash -lc "git clone -q $RepoUrl ~/$RepoDir"
        }
    }

    Invoke-Step "Setting COURSE_HOME in ~/.bashrc" {
        wsl.exe -d $Distro -- bash -lc "grep -q 'COURSE_HOME' ~/.bashrc || echo 'export COURSE_HOME=`$HOME/$RepoDir' >> ~/.bashrc"
    }

    Write-Step "Running the Linux installer inside $Distro - this takes 10-15 minutes"
    Write-Step "(it installs Docker, kind, kubectl, Terraform, Ansible, Trivy, Conftest, act)"
    if (-not $DryRun) {
        wsl.exe -d $Distro -- bash -lc "cd ~/$RepoDir && ./lab-setup/install-ubuntu24.sh"
        if ($LASTEXITCODE -ne 0) {
            Write-Err "The Linux installer reported a problem. Open Ubuntu and re-run:"
            Write-Err "  cd ~/$RepoDir && ./lab-setup/install-ubuntu24.sh"
            exit 1
        }
    }
}

# ------------------------------------------------------------------ done
Write-Host ""
Write-Ok "Windows setup complete."
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor White
Write-Host "    1. Close this window and open '$Distro' from the Start menu."
Write-Host "    2. Log out and back in once (or run: newgrp docker) so Docker group"
Write-Host "       membership takes effect."
Write-Host "    3. Verify:  cd ~/$RepoDir && ./lab-setup/check-environment.sh"
Write-Host "    4. Then follow labs/lab-day1/README.md - every command is the same"
Write-Host "       as on Linux, because you are running Linux."
Write-Host ""
Write-Host "  Anything you publish on a port inside Ubuntu (8080, 9090, 3000,"
Write-Host "  30080 ...) is reachable from your Windows browser at http://localhost:<port>."
Write-Host ""
