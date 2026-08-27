# Windows Edition

**The Ubuntu course material is unchanged.** On Windows you set up Ubuntu
24.04 inside WSL2 and then follow the normal instructions — every command in
every lab is identical, because you are running Linux.

This file and the four below are the whole Windows addition; nothing in the
Linux path was modified for it.

## Quick start

```powershell
# 1. ADMINISTRATOR PowerShell, from the cloned repo:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\lab-setup\install-windows.ps1
```

```powershell
# 2. verify both halves (Windows side, then inside Ubuntu):
.\lab-setup\check-windows.ps1
```

Then open **Ubuntu-24.04** from the Start menu and follow the normal course
instructions from `README.md` and `labs/`.

## The Windows files

| File | What it is |
|------|------------|
| [`lab-setup/install-windows.ps1`](lab-setup/install-windows.ps1) | Installs WSL2 + Ubuntu-24.04, sizes the VM, enables systemd, clones the repo inside Linux and runs the normal `install-ubuntu24.sh`. Idempotent; supports `-DryRun`. |
| [`lab-setup/check-windows.ps1`](lab-setup/check-windows.ps1) | Preflight for the Windows side, then runs the normal `check-environment.sh` inside Ubuntu. |
| [`lab-setup/WINDOWS.md`](lab-setup/WINDOWS.md) | Setup guide: requirements, what the installer does, why WSL2, troubleshooting, and what to do if WSL is blocked by policy. |
| [`labs/WINDOWS.md`](labs/WINDOWS.md) | Running the labs: which terminal, where files live, the port-to-browser table, and a PowerShell fallback for machines without WSL. |
| [`lab-setup/tests/Test-WindowsSetup.ps1`](lab-setup/tests/Test-WindowsSetup.ps1) | Exercises the installer's logic off-Windows (24 assertions, 9 scenarios). |

## Why WSL2 rather than native Windows

Native Windows was considered and rejected as the supported path:

- **Ansible cannot run on Windows as a control node**, so Lab Day 1 Part F
  would be impossible.
- Every `sed`, heredoc and shell loop in both labs would need rewriting, and
  then maintaining as a second set of instructions that drifts.

With WSL2 there is one set of lab instructions for everyone.

**Docker Desktop is not required** — Docker Engine is installed *inside* the
Ubuntu distro by the normal course installer, which avoids Docker Desktop
licensing entirely.

## Requirements and lead time

- Windows 10 build 19041+ or Windows 11
- Hardware virtualisation enabled in BIOS/UEFI
- 8 GB RAM (16 GB comfortable), 25 GB free disk
- Local administrator rights for the setup only

> **Check virtualisation and WSL policy a week before the course, not on the
> morning.** On managed corporate laptops both can need IT involvement, and
> if WSL is blocked by policy that participant needs a Linux VM instead —
> see the fallback ladder in [`lab-setup/WINDOWS.md`](lab-setup/WINDOWS.md).

## Verification status

| | |
|---|---|
| PowerShell syntax | parsed clean |
| PSScriptAnalyzer | no errors |
| Installer logic | 24 assertions across 9 scenarios, all passing |
| On a real Windows machine | **not yet — do one dry run before the course** |
