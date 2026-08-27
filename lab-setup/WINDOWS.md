# Running the Course on Windows

**Short version:** you run the labs inside **Ubuntu 24.04 on WSL2**. Every
command in every lab is then exactly the same as for Linux participants,
because you *are* running Linux. No lab has a separate "Windows version".

Two PowerShell scripts do the setup:

```powershell
# In an ADMINISTRATOR PowerShell window, from the repo folder:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\lab-setup\install-windows.ps1
```

```powershell
.\lab-setup\check-windows.ps1
```

---

## Why WSL2 and not "native Windows"

| | WSL2 (supported) | Native Windows |
|---|---|---|
| Lab commands | identical to Linux | every `sed`, heredoc and shell loop must be rewritten |
| **Ansible** (Day 1 Part F) | works | **impossible** — Windows cannot be an Ansible control node |
| Docker | Docker Engine inside Ubuntu | Docker Desktop, which needs a **paid licence** in larger organisations |
| kind / kubectl | work | work |
| act | works | works |
| Terraform / Trivy / Conftest | work | work |

The Ansible row is the decisive one: a whole lab part is simply unavailable
without a Linux control node. WSL2 gives you that for free.

**Docker Desktop is not required.** The course installer puts Docker Engine
*inside* your Ubuntu distro, which sidesteps Docker Desktop licensing
entirely. If your organisation already licenses Docker Desktop you may use it
instead — enable *Settings → Resources → WSL Integration* for `Ubuntu-24.04`
and skip Docker in the Linux installer.

---

## What the installer does

1. Checks Windows build, virtualisation, RAM and disk.
2. Installs WSL2 and the `Ubuntu-24.04` distro if they are missing.
3. Writes `%UserProfile%\.wslconfig` giving the Linux VM **6 GB RAM, 4 CPUs**.
4. Enables **systemd** inside the distro (`/etc/wsl.conf`) — Docker needs it.
5. Clones the course repo to `~/devops-course` inside Ubuntu, sets
   `COURSE_HOME`, and runs `lab-setup/install-ubuntu24.sh`.

It is safe to re-run: every step checks whether it is already done. Use
`-DryRun` to see what it would do.

> **You will be asked to reboot once**, after WSL is first installed, and to
> open the Ubuntu app once to create your Linux username and password. Run the
> script again afterwards and it picks up where it left off.

---

## Requirements

- Windows 10 build 19041 (version 2004) or newer, or Windows 11
- Hardware virtualisation enabled in BIOS/UEFI (**a corporate laptop may need
  IT to enable this** — check before the course, not on the morning)
- 8 GB RAM minimum, 16 GB comfortable
- 25 GB free disk
- Local administrator rights for the *setup only*; the labs need none

---

## Day-to-day: how the labs feel on Windows

**Open a terminal.** Start menu → **Ubuntu-24.04**, or Windows Terminal and
pick the Ubuntu tab. Everything happens there.

```bash
cd "$COURSE_HOME"          # ~/devops-course
./lab-setup/check-environment.sh
```

**Browser URLs just work.** WSL2 forwards published ports to Windows, so
anything a lab publishes is reachable from Edge/Chrome on Windows:

| Lab | URL on Windows |
|-----|----------------|
| Order service (Compose) | <http://localhost:8080> |
| Deployed by the pipeline | <http://localhost:8081> |
| Terraform-managed service | <http://localhost:8090> |
| Kubernetes NodePort (kind) | <http://localhost:30080> |
| Prometheus | <http://localhost:9090> |
| Grafana | <http://localhost:3000> |
| Gitea pipeline UI (Day 1 Part H) | <http://localhost:3001> |

**Keep your files in Linux, not on C:.** Work in `~/devops-course` inside
Ubuntu. Using `/mnt/c/...` is several times slower and breaks file permissions
that Docker cares about.

**Editing files.** Install VS Code on Windows plus the **WSL** extension, then
from your Ubuntu terminal:

```bash
code .
```

VS Code opens on Windows while the files, terminal and tools stay in Linux.

**Copy and paste.** In Windows Terminal, `Ctrl+Shift+V` pastes. Every lab step
is a paste-able command, so this is the only shortcut you need.

---

## Windows-specific troubleshooting

| Symptom | Fix |
|---------|-----|
| `wsl` is not recognised | Run `install-windows.ps1` as administrator; reboot when it says to. |
| "Virtualisation not enabled" | Enable Intel VT-x / AMD-V in BIOS/UEFI. On a managed laptop, ask IT. |
| WSL installs but the distro never appears | Open the **Ubuntu-24.04** app from the Start menu once to finish first-run setup. |
| `docker: Cannot connect to the Docker daemon` inside Ubuntu | systemd is probably off. `grep systemd /etc/wsl.conf`, then from PowerShell: `wsl --shutdown`, reopen Ubuntu. |
| `permission denied` on docker | `newgrp docker`, or close and reopen the Ubuntu window. |
| kind cluster fails or is very slow | Give WSL more memory in `%UserProfile%\.wslconfig`, then `wsl --shutdown`. |
| Ports not reachable from the Windows browser | `wsl --shutdown` and reopen; check the service is really published (`docker ps`). |
| Everything is slow | You are probably working under `/mnt/c/`. Move the repo into `~` inside Ubuntu. |
| Corporate VPN breaks WSL networking | Common with split-tunnel VPNs. Disconnect the VPN for the labs, or ask IT for the WSL-friendly profile. |

---

## If WSL2 is genuinely blocked by policy

Some locked-down estates will not allow WSL. In that case, in order of
preference:

1. **A Linux VM** — Hyper-V, VMware or VirtualBox running Ubuntu 24.04, then
   follow the normal Linux instructions inside it. This is the closest
   equivalent and everything works.
2. **A cloud VM** for the two days (any provider, 4 vCPU / 8 GB), same Linux
   instructions.
3. **Native Windows, partial labs** — Docker Desktop, kind, kubectl,
   Terraform, Trivy, Conftest and act all have Windows builds and the
   container/Kubernetes/scanning parts work in PowerShell with adjusted
   syntax. **Ansible does not run**, and the shell-based steps
   (`sed`, heredocs, `for` loops) need rewriting as you go. Treat this as a
   fallback for observing, not for the full hands-on experience.

Tell your instructor before the course if you land on option 3, so they can
pair you with someone on WSL for the affected parts.
