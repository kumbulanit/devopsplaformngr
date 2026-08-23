# Verification image based on the latest Ubuntu LTS.
# This container validates that the course package installs and runs end-to-end on Ubuntu.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install base tooling.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    git \
    unzip \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI and Compose v2 plugin from the Ubuntu repositories.
# This keeps the verification container robust on Ubuntu 24.04 without relying
# on third-party repository certificates during the image build.
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker.io docker-compose-v2 && \
    rm -rf /var/lib/apt/lists/*

# Copy the course package into the image (includes verify/bin/ with pre-downloaded tools).
WORKDIR /workspace
COPY . /workspace

# Install Terraform, kind and kubectl from the host-downloaded binaries so the
# image build does not depend on third-party repository availability.
RUN install -o root -g root -m 0755 /workspace/verify/bin/terraform /usr/local/bin/terraform && \
    install -o root -g root -m 0755 /workspace/verify/bin/kind /usr/local/bin/kind && \
    install -o root -g root -m 0755 /workspace/verify/bin/kubectl /usr/local/bin/kubectl

# Make scripts executable.
RUN chmod +x /workspace/verify/entrypoint.sh && \
    chmod +x /workspace/labs/lab09-capstone/run-capstone.sh || true

# Run the verification script by default.
CMD ["/workspace/verify/entrypoint.sh"]
