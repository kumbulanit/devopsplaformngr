# Lab setup helpers

This folder contains Ubuntu 24.04 setup automation for the course environment.

## Install everything

From the repository root:

```bash
chmod +x lab-setup/install-ubuntu24.sh
./lab-setup/install-ubuntu24.sh
```

Use `--dry-run` to preview the commands without changing the machine:

```bash
./lab-setup/install-ubuntu24.sh --dry-run
```

The installer sets up:

- Git, curl, CA certificates, gnupg, Python 3, pip, and venv
- Docker Engine with the Compose plugin
- kind
- kubectl
- Terraform
- The Python virtual environment for the sample app in `labs/app/.venv`

## Create the lab directories

From the repository root:

```bash
chmod +x lab-setup/create-labs.sh
./lab-setup/create-labs.sh
```

This script creates or confirms the `labs/lab00-environment-setup` through `labs/lab08-observability` directories and adds a starter `README.md` if a lab folder is missing.
