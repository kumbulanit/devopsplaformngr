#!/usr/bin/env bash
# Download tooling binaries on the host so the Ubuntu Dockerfile does not need
# to fetch them over HTTPS inside the build container.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${SCRIPT_DIR}/bin"
mkdir -p "${BIN_DIR}"

ARCH="amd64"
# Detect the host architecture so the downloaded binaries match the container
# architecture (the verify Dockerfile uses ubuntu:24.04, which defaults to the
# host architecture on Apple Silicon and x86_64 machines).
if [ "$(uname -m)" = "arm64" ]; then
  ARCH="arm64"
fi

echo "Downloading Terraform..."
curl -fsSL "https://releases.hashicorp.com/terraform/1.9.4/terraform_1.9.4_linux_${ARCH}.zip" -o "${BIN_DIR}/terraform.zip"
unzip -o "${BIN_DIR}/terraform.zip" -d "${BIN_DIR}"
rm "${BIN_DIR}/terraform.zip"

echo "Downloading kind..."
curl -fsSL "https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-${ARCH}" -o "${BIN_DIR}/kind"
chmod +x "${BIN_DIR}/kind"

echo "Downloading kubectl..."
curl -fsSL "https://dl.k8s.io/release/v1.30.3/bin/linux/${ARCH}/kubectl" -o "${BIN_DIR}/kubectl"
chmod +x "${BIN_DIR}/kubectl"

echo "Binaries prepared in ${BIN_DIR}"
