<#
.SYNOPSIS
    Prepare a Windows machine for the DevOps & Platform Engineering course.

.DESCRIPTION
    The course runs on Ubuntu 24.04. On Windows the supported route is WSL2:
    a real Ubuntu 24.04 kernel inside Windows, where every lab command works
    unchanged and Ansible (Lab Day 1 Part F) can run at all.

    This script:
      1. checks Windows version, virtualisation, RAM and disk
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

.PARAMETER LoadFunctionsOnly
    Define the functions but do not run anything. Used by the test harness in
    tests/Test-WindowsSetup.ps1 so the logic can be exercised off-Windows.

.EXAMPLE
    # In an ADMINISTRATOR PowerShell window:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
    .\install-windows.ps1
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$SkipCourseInstall,
    [switch]$LoadFunctionsOnly
)

$ErrorActionPreference = 'Stop'

$script:Distro  = 'Ubuntu-24.04'
$script:RepoUrl = 'https://github.com/kumbulanit/devopsplaformngr.git'
$script:RepoDir = 'devops-course'

# --------------------------------------------------------------- output
function Write-Step  { param($m) Write-Host "[labsetup] $m" -ForegroundColor Cyan }
function Write-Ok    { param($m) Write-Host "[labsetup] $m" -ForegroundColor Green }
function Write-Warn2 { param($m) Write-Host "[labsetup] $m" -ForegroundColor Yellow }
function Write-Err   { param($m) Write-Host "[labsetup] $m" -ForegroundColor Red }

# ------------------------------------------------------- environment probes
# Each probe is its own function so the test harness can replace it.

function Test-IsAdmin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-WindowsBuild {
    [int](Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').CurrentBuildNumber
}

function Get-WindowsCaption { (Get-CimInstance Win32_OperatingSystem).Caption }

function Test-Virtualisation {
    $hyper = (Get-CimInstance Win32_ComputerSystem).HypervisorPresent
    $virt  = (Get-CimInstance Win32_Processor | Select-Object -First 1).VirtualizationFirmwareEnabled
    [bool]($hyper -or $virt)
}

function Get-FreeDiskGB { [math]::Round((Get-PSDrive C).Free / 1GB, 1) }

function Get-RamGB {
    [math]::Round((Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize / 1MB, 1)
}

function Test-WslPresent { $null -ne (Get-Command wsl.exe -ErrorAction SilentlyContinue) }

# All wsl.exe traffic goes through here, so the harness can record it.
# Uses $args rather than a declared parameter: a typed
# ValueFromRemainingArguments parameter swallows switch-looking tokens such
# as "-d", which would turn "wsl --install -d Ubuntu-24.04" into
# "wsl --install Ubuntu-24.04" and fail.
function Invoke-Wsl { & wsl.exe @args }

function Get-WslDistros {
    (Invoke-Wsl --list --quiet) -replace "`0", "" |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ }
}

function Test-WslCommand {
    # Runs a bash test inside the distro; returns $true when it echoes "yes".
    param([string]$BashTest)
    ((Invoke-Wsl -d $script:Distro -- bash -lc $BashTest) | Out-String).Trim() -eq 'yes'
}

function Get-WslConfigPath { Join-Path $env:USERPROFILE '.wslconfig' }

# ------------------------------------------------------------------ helpers
function Invoke-Step {
    param([string]$Description, [scriptblock]$Action, [switch]$DryRun)
    Write-Step $Description
    if ($DryRun) { Write-Host "           (dry run - skipped)" -ForegroundColor DarkGray; return }
    # Out-Host, not the pipeline: otherwise the action's output becomes part of
    # this function's return value and the caller's exit code turns into an array.
    & $Action | Out-Host
}

# ------------------------------------------------------------------- main
function Install-CourseOnWindows {
    [CmdletBinding()]
    param([switch]$DryRun, [switch]$SkipCourseInstall)

    Write-Host ""
    Write-Host "DevOps & Platform Engineering - Windows setup" -ForegroundColor White
    Write-Host "=============================================" -ForegroundColor White
    Write-Host ""
    if ($DryRun) { Write-Warn2 "DRY RUN: nothing will be changed." }

    # --- 0. the machine itself
    if (-not (Test-IsAdmin)) {
        Write-Err "This script must run in an ADMINISTRATOR PowerShell window."
        Write-Err "Right-click PowerShell -> 'Run as administrator', then run it again."
        return 1
    }

    $build = Get-WindowsBuild
    Write-Step "Windows: $(Get-WindowsCaption) (build $build)"
    if ($build -lt 19041) {
        Write-Err "WSL2 needs Windows 10 build 19041 (version 2004) or newer. Update Windows first."
        return 1
    }

    if (-not (Test-Virtualisation)) {
        Write-Err "Hardware virtualisation is disabled. Enable Intel VT-x / AMD-V in the BIOS/UEFI."
        Write-Err "On a corporate laptop this may need your IT team."
        return 1
    }
    Write-Ok "Virtualisation is available"

    $freeGB = Get-FreeDiskGB
    Write-Step "Free space on C: ${freeGB} GB"
    if ($freeGB -lt 25) { Write-Warn2 "Less than 25 GB free. The course needs ~20 GB of images." }

    $ramGB = Get-RamGB
    Write-Step "Physical RAM: ${ramGB} GB"
    if ($ramGB -lt 8) { Write-Warn2 "8 GB or more is recommended (WSL2 takes 6 GB of it)." }

    # --- 1. WSL itself
    if (-not (Test-WslPresent)) {
        Invoke-Step "Installing WSL2 and $script:Distro" -DryRun:$DryRun {
            Invoke-Wsl --install -d $script:Distro | Out-Host
        }
        Write-Warn2 ""
        Write-Warn2 "WSL was just installed. REBOOT WINDOWS NOW, then:"
        Write-Warn2 "  1. open the Ubuntu app from the Start menu and create your Linux user"
        Write-Warn2 "  2. run this script again to finish the setup"
        Write-Warn2 ""
        return 0
    }
    Write-Ok "WSL is present"
    Invoke-Step "Ensuring WSL defaults to version 2" -DryRun:$DryRun {
        Invoke-Wsl --set-default-version 2 | Out-Null
    }

    # --- 2. the Ubuntu distro
    $distros = Get-WslDistros
    if ($distros -contains $script:Distro) {
        Write-Ok "$script:Distro is already installed"
    } else {
        Invoke-Step "Installing the $script:Distro distro" -DryRun:$DryRun {
            Invoke-Wsl --install -d $script:Distro --no-launch | Out-Host
        }
        Write-Warn2 ""
        Write-Warn2 "Now open '$script:Distro' from the Start menu once, create your Linux"
        Write-Warn2 "username and password, then re-run this script."
        Write-Warn2 ""
        return 0
    }
    Invoke-Step "Making $script:Distro the default distro" -DryRun:$DryRun {
        Invoke-Wsl --set-default $script:Distro | Out-Null
    }

    # --- 3. memory for the Linux VM
    $wslConfig = Get-WslConfigPath
    if (Test-Path $wslConfig) {
        Write-Ok ".wslconfig already exists (leaving it alone): $wslConfig"
    } else {
        Invoke-Step "Writing $wslConfig so the labs get enough memory" -DryRun:$DryRun {
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

    # --- 4. systemd, which Docker needs
    if (Test-WslCommand "grep -qs 'systemd=true' /etc/wsl.conf && echo yes || echo no") {
        Write-Ok "systemd is already enabled inside $script:Distro"
    } else {
        Invoke-Step "Enabling systemd inside $script:Distro (Docker needs it)" -DryRun:$DryRun {
            Invoke-Wsl -d $script:Distro -- bash -lc "printf '[boot]\nsystemd=true\n' | sudo tee /etc/wsl.conf >/dev/null" | Out-Host
        }
        Invoke-Step "Restarting WSL so systemd starts" -DryRun:$DryRun { Invoke-Wsl --shutdown | Out-Host }
        if (-not $DryRun) { Start-Sleep -Seconds 8 }
    }

    # --- 5. the course itself
    if ($SkipCourseInstall) {
        Write-Ok "Skipping the course install (-SkipCourseInstall)"
        return 0
    }

    Invoke-Step "Installing git inside $script:Distro" -DryRun:$DryRun {
        Invoke-Wsl -d $script:Distro -- bash -lc "command -v git >/dev/null || (sudo apt-get update -qq && sudo apt-get install -y -qq git)" | Out-Host
    }

    if (Test-WslCommand "[ -d ~/$script:RepoDir/lab-setup ] && echo yes || echo no") {
        Write-Ok "Course repository already cloned at ~/$script:RepoDir"
    } else {
        Invoke-Step "Cloning the course repository into ~/$script:RepoDir" -DryRun:$DryRun {
            Invoke-Wsl -d $script:Distro -- bash -lc "git clone -q $script:RepoUrl ~/$script:RepoDir" | Out-Host
        }
    }

    Invoke-Step "Setting COURSE_HOME in ~/.bashrc" -DryRun:$DryRun {
        Invoke-Wsl -d $script:Distro -- bash -lc "grep -q COURSE_HOME ~/.bashrc || echo 'export COURSE_HOME=`$HOME/$script:RepoDir' >> ~/.bashrc" | Out-Host
    }

    Write-Step "Running the Linux installer inside $script:Distro - 10-15 minutes"
    Write-Step "(Docker, kind, kubectl, Terraform, Ansible, Trivy, Conftest, act)"
    if (-not $DryRun) {
        Invoke-Wsl -d $script:Distro -- bash -lc "cd ~/$script:RepoDir && ./lab-setup/install-ubuntu24.sh" | Out-Host
        if ($LASTEXITCODE -ne 0) {
            Write-Err "The Linux installer reported a problem. Open Ubuntu and re-run:"
            Write-Err "  cd ~/$script:RepoDir && ./lab-setup/install-ubuntu24.sh"
            return 1
        }
    }

    Write-Host ""
    Write-Ok "Windows setup complete."
    Write-Host ""
    Write-Host "  Next steps:" -ForegroundColor White
    Write-Host "    1. Close this window and open '$script:Distro' from the Start menu."
    Write-Host "    2. Log out and back in once (or run: newgrp docker) so Docker group"
    Write-Host "       membership takes effect."
    Write-Host "    3. Verify:  cd ~/$script:RepoDir && ./lab-setup/check-environment.sh"
    Write-Host "    4. Then follow labs/lab-day1/README.md - every command is the same"
    Write-Host "       as on Linux, because you are running Linux."
    Write-Host ""
    Write-Host "  Anything published on a port inside Ubuntu (8080, 9090, 3000, 30080 ...)"
    Write-Host "  is reachable from your Windows browser at http://localhost:<port>."
    Write-Host ""
    return 0
}

if (-not $LoadFunctionsOnly) {
    # Select-Object -Last 1 defends the exit code against any stray output.
    $code = @(Install-CourseOnWindows -DryRun:$DryRun -SkipCourseInstall:$SkipCourseInstall) |
        Select-Object -Last 1
    exit ([int]$code)
}
