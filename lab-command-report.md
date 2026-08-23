# Lab Command Verification Report

Generated: 2026-08-12T12:18:42.335497+00:00Z

| Lab | # | Directory | Command | Status | Notes |
|-----|---|-----------|---------|--------|-------|
| lab00-environment-setup | 1 | . | `brew install git docker --cask docker` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 2 | . | `brew install docker-compose kind kubectl terraform python` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 3 | . | `sudo apt-get update` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 4 | . | `sudo apt-get install -y git curl ca-certificates gnupg lsb-release` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 5 | . | `sudo apt-get install -y docker.io docker-compose-v2` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 6 | . | `sudo systemctl enable --now docker` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 7 | . | `sudo usermod -aG docker "$USER"` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 8 | . | `ARCH=$(dpkg --print-architecture)` | FAIL | exit code 127 |
| | | | | | Output: `/bin/sh: dpkg: command not found` |
| lab00-environment-setup | 9 | . | `curl -Lo ./kind "https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-${ARCH}"` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 10 | . | `chmod +x ./kind && sudo mv ./kind /usr/local/bin/kind` | FAIL | exit code 1 |
| | | | | | Output: `sudo: a terminal is required to read the password; either use the -S option to read from standard input or configure an ` |
| lab00-environment-setup | 11 | . | `curl -LO "https://dl.k8s/release/$(curl -L -s https://dl.k8s/release/stable.txt)/bin/linux/${ARCH}/kubectl"` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 12 | . | `sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 13 | . | `rm kubectl` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 14 | . | `curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 15 | . | `echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 16 | . | `sudo apt-get update && sudo apt-get install -y terraform` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 17 | . | `git --version` | PASS |  |
| lab00-environment-setup | 18 | . | `docker --version` | PASS |  |
| lab00-environment-setup | 19 | . | `docker run --rm hello-world` | PASS |  |
| lab00-environment-setup | 20 | . | `docker compose version` | PASS |  |
| lab00-environment-setup | 21 | . | `kind version` | PASS |  |
| lab00-environment-setup | 22 | . | `kubectl version --client` | PASS |  |
| lab00-environment-setup | 23 | . | `terraform -version` | FAIL | exit code 126 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab00-environment-setup | 24 | . | `python3 --version` | PASS |  |
| lab00-environment-setup | 25 | . | `python3 -m pip --version` | PASS |  |
| lab00-environment-setup | 26 | labs/app | `python3 -m venv .venv` | PASS |  |
| lab00-environment-setup | 27 | labs/app | `source .venv/bin/activate        # Windows: .venv\Scripts\activate` | PASS |  |
| lab00-environment-setup | 28 | labs/app | `pip install -r requirements.txt` | FAIL | exit code 127 |
| | | | | | Output: `/bin/sh: pip: command not found` |
| lab00-environment-setup | 29 | labs/app | `uvicorn main:app --reload --port 8000` | PASS | Background PID 99376 |
| lab00-environment-setup | 30 | labs/app | `curl http://localhost:8000/health` | FAIL | exit code 7 |
| | | | | | Output: `% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current                                  Dload  Up` |
| lab00-environment-setup | 31 | labs/app | `curl -X POST http://localhost:8000/orders \;   -H "Content-Type: application/json" \;   -d '{"item":"coffee","quantity":2,"price":3.5}'` | FAIL | exit code 7 |
| | | | | | Output: `% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current                                  Dload  Up` |
| lab00-environment-setup | 32 | labs/app | `kind create cluster --name devops-course` | PASS |  |
| lab00-environment-setup | 33 | labs/app | `kubectl get nodes` | PASS |  |
| lab00-environment-setup | 34 | labs/app | `kind delete cluster --name devops-course` | PASS |  |
| lab00-environment-setup | 35 | labs/app | `brew install act        # macOS` | SKIP | Classification: skip-os-specific |
| lab00-environment-setup | 36 | labs/app | `choco install act-cli   # Windows` | SKIP | Classification: skip-os-specific |
| lab01-git-collaboration | 1 | labs/app | `rm -rf .git` | PASS |  |
| lab01-git-collaboration | 2 | labs/app | `git init` | PASS |  |
| lab01-git-collaboration | 3 | labs/app | `git add .` | PASS |  |
| lab01-git-collaboration | 4 | labs/app | `git commit -m "Initial order and payment services"` | PASS |  |
| lab01-git-collaboration | 5 | labs/app | `git checkout -b feature/health-service-name` | PASS |  |
| lab01-git-collaboration | 6 | labs/app | `source .venv/bin/activate` | PASS |  |
| lab01-git-collaboration | 7 | labs/app | `pytest` | FAIL | exit code 127 |
| | | | | | Output: `/bin/sh: pytest: command not found` |
| lab01-git-collaboration | 8 | labs/app | `git add main.py` | PASS |  |
| lab01-git-collaboration | 9 | labs/app | `git commit -m "feat: add service_name to health endpoint"` | FAIL | exit code 1 |
| | | | | | Output: `On branch feature/health-service-name nothing to commit, working tree clean` |
| lab01-git-collaboration | 10 | /tmp | `git clone --bare /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/labs/app review-repo.git` | FAIL | exit code 129 |
| | | | | | Output: `fatal: Too many arguments.  usage: git clone [<options>] [--] <repo> [<dir>]` |
| lab01-git-collaboration | 11 | /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/labs/app | `git remote add local /tmp/review-repo.git` | PASS |  |
| lab01-git-collaboration | 12 | /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/labs/app | `git push local feature/health-service-name` | FAIL | exit code 128 |
| | | | | | Output: `fatal: '/tmp/review-repo.git' does not appear to be a git repository fatal: Could not read from remote repository. ` |
| lab01-git-collaboration | 13 | /tmp | `git clone review-repo.git reviewer-copy` | FAIL | exit code 128 |
| | | | | | Output: `fatal: repository 'review-repo.git' does not exist` |
| lab01-git-collaboration | 14 | reviewer-copy | `git fetch --all` | FAIL | Execution error: [Errno 2] No such file or directory: PosixPath('/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/reviewer-copy') |
| lab01-git-collaboration | 15 | reviewer-copy | `git checkout feature/health-service-name` | FAIL | Execution error: [Errno 2] No such file or directory: PosixPath('/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/reviewer-copy') |
| lab01-git-collaboration | 16 | reviewer-copy | `git diff main..feature/health-service-name` | FAIL | Execution error: [Errno 2] No such file or directory: PosixPath('/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/reviewer-copy') |
| lab01-git-collaboration | 17 | reviewer-copy | `git checkout main` | FAIL | Execution error: [Errno 2] No such file or directory: PosixPath('/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/reviewer-copy') |
| lab01-git-collaboration | 18 | reviewer-copy | `git merge --no-ff feature/health-service-name -m "Merge feature/health-service-name"` | FAIL | Execution error: [Errno 2] No such file or directory: PosixPath('/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/reviewer-copy') |
| lab01-git-collaboration | 19 | reviewer-copy | `git push local main` | FAIL | Execution error: [Errno 2] No such file or directory: PosixPath('/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/reviewer-copy') |
| lab01-git-collaboration | 20 | reviewer-copy | `git log --oneline --graph --all` | FAIL | Execution error: [Errno 2] No such file or directory: PosixPath('/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/reviewer-copy') |
| lab01-git-collaboration | 21 | reviewer-copy | `pytest` | FAIL | Execution error: [Errno 2] No such file or directory: PosixPath('/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/reviewer-copy') |
| lab01-git-collaboration | 22 | reviewer-copy | `cat > .git/hooks/commit-msg <<'EOF'; if grep -E 'TODO|FIXME' "$1" && ! grep -E '#[0-9]+' "$1"; then;   echo "Commit message with TODO/FIXME must include a ticket ID";   exit 1; fi; EOF` | FAIL | Execution error: [Errno 2] No such file or directory: PosixPath('/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/reviewer-copy') |
| lab01-git-collaboration | 23 | reviewer-copy | `chmod +x .git/hooks/commit-msg` | FAIL | Execution error: [Errno 2] No such file or directory: PosixPath('/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/reviewer-copy') |
| lab02-docker-basics | 1 | . | `docker build -t order-service:lab02 --build-arg BUILD_ID=lab02 -f Dockerfile .` | FAIL | exit code 1 |
| | | | | | Output: `#0 building with "orbstack" instance using docker driver  #1 [internal] load build definition from Dockerfile` |
| lab02-docker-basics | 2 | . | `docker images order-service` | PASS |  |
| lab02-docker-basics | 3 | . | `docker run -d --name order-lab02 -p 8080:8000 order-service:lab02` | PASS |  |
| lab02-docker-basics | 4 | . | `curl http://localhost:8080/health` | FAIL | exit code 52 |
| | | | | | Output: `% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current                                  Dload  Up` |
| lab02-docker-basics | 5 | . | `docker ps` | PASS |  |
| lab02-docker-basics | 6 | . | `docker logs order-lab02` | PASS |  |
| lab02-docker-basics | 7 | . | `docker exec -it order-lab02 /bin/sh` | PASS |  |
| lab02-docker-basics | 8 | . | `whoami` | PASS |  |
| lab02-docker-basics | 9 | . | `ls -la /app` | FAIL | exit code 1 |
| | | | | | Output: `ls: /app: No such file or directory` |
| lab02-docker-basics | 10 | . | `exit` | PASS |  |
| lab02-docker-basics | 11 | . | `docker history order-service:lab02` | PASS |  |
| lab02-docker-basics | 12 | . | `docker stop order-lab02` | PASS |  |
| lab02-docker-basics | 13 | . | `docker rm order-lab02` | PASS |  |
| lab02-docker-basics | 14 | . | `brew install dive          # macOS` | SKIP | Classification: skip-os-specific |
| lab02-docker-basics | 15 | . | `dive order-service:lab02` | FAIL | exit code 1 |
| | | | | | Output: `[1mImage Source: [0mdocker://order-service:lab02 [1mExtracting image from docker-engine...[0m (this can take a while` |
| lab03-compose-microservices | 1 | . | `docker compose up -d --build` | FAIL | exit code 1 |
| | | | | | Output: `no configuration file provided: not found` |
| lab03-compose-microservices | 2 | . | `docker compose ps` | FAIL | exit code 1 |
| | | | | | Output: `no configuration file provided: not found` |
| lab03-compose-microservices | 3 | . | `curl -X POST http://localhost:8080/orders \;   -H "Content-Type: application/json" \;   -d '{"item":"latte","quantity":1,"price":4.0}'` | FAIL | exit code 7 |
| | | | | | Output: `% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current                                  Dload  Up` |
| lab03-compose-microservices | 4 | . | `curl http://localhost:8080/orders` | FAIL | exit code 7 |
| | | | | | Output: `% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current                                  Dload  Up` |
| lab03-compose-microservices | 5 | . | `docker network ls` | PASS |  |
| lab03-compose-microservices | 6 | . | `docker network inspect app_app-network  # name may vary; look for app-network` | FAIL | exit code 1 |
| | | | | | Output: `[] Error response from daemon: network app_app-network not found` |
| lab03-compose-microservices | 7 | . | `docker compose up -d --scale payment-service=2` | FAIL | exit code 1 |
| | | | | | Output: `no configuration file provided: not found` |
| lab03-compose-microservices | 8 | . | `BUILD_ID=compose-demo docker compose up -d --build` | FAIL | exit code 1 |
| | | | | | Output: `no configuration file provided: not found` |
| lab03-compose-microservices | 9 | . | `curl http://localhost:8080/health` | FAIL | exit code 7 |
| | | | | | Output: `% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current                                  Dload  Up` |
| lab03-compose-microservices | 10 | . | `docker compose down --volumes` | FAIL | exit code 1 |
| | | | | | Output: `no configuration file provided: not found` |
| lab04-cicd-github-actions | 1 | . | `cp labs/lab04-cicd-github-actions/.github/workflows/ci.yml .github/workflows/ci.yml` | FAIL | exit code 1 |
| | | | | | Output: `cp: .github/workflows/ci.yml: No such file or directory` |
| lab04-cicd-github-actions | 2 | . | `git add .github/workflows/ci.yml` | FAIL | exit code 128 |
| | | | | | Output: `fatal: not a git repository (or any of the parent directories): .git` |
| lab04-cicd-github-actions | 3 | . | `git commit -m "Add CI workflow for order service"` | FAIL | exit code 128 |
| | | | | | Output: `fatal: not a git repository (or any of the parent directories): .git` |
| lab04-cicd-github-actions | 4 | . | `git push origin main` | SKIP | Classification: skip-no-remote |
| lab04-cicd-github-actions | 5 | . | `git checkout -b ci-demo` | FAIL | exit code 128 |
| | | | | | Output: `fatal: not a git repository (or any of the parent directories): .git` |
| lab04-cicd-github-actions | 6 | . | `echo "# CI demo branch" >> labs/app/main.py` | PASS |  |
| lab04-cicd-github-actions | 7 | . | `git add labs/app/main.py` | FAIL | exit code 128 |
| | | | | | Output: `fatal: not a git repository (or any of the parent directories): .git` |
| lab04-cicd-github-actions | 8 | . | `git commit -m "Demo change to trigger CI"` | FAIL | exit code 128 |
| | | | | | Output: `fatal: not a git repository (or any of the parent directories): .git` |
| lab04-cicd-github-actions | 9 | . | `git push origin ci-demo` | SKIP | Classification: skip-no-remote |
| lab04-cicd-github-actions | 10 | . | `brew install act` | SKIP | Classification: skip-os-specific |
| lab04-cicd-github-actions | 11 | . | `act -j test` | SKIP | Classification: skip-tool-missing |
| lab04-cicd-github-actions | 12 | . | `act -j build` | SKIP | Classification: skip-tool-missing |
| lab04-cicd-github-actions | 13 | . | `act -j security-scan` | SKIP | Classification: skip-tool-missing |
| lab05-iac-terraform | 1 | labs/app | `docker build -t order-service:lab02 --build-arg BUILD_ID=lab02 -f Dockerfile .` | PASS |  |
| lab05-iac-terraform | 2 | labs/app | `docker build -t payment-service:lab02 --build-arg BUILD_ID=lab02 -f Dockerfile.payment .` | PASS |  |
| lab05-iac-terraform | 3 | labs/lab05-iac-terraform | `cp terraform.tfvars.example terraform.tfvars` | PASS |  |
| lab05-iac-terraform | 4 | labs/lab05-iac-terraform | `terraform init` | FAIL | exit code 126 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 5 | labs/lab05-iac-terraform | `terraform plan -out=tfplan` | FAIL | exit code 126 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 6 | labs/lab05-iac-terraform | `terraform apply tfplan` | FAIL | exit code 126 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 7 | labs/lab05-iac-terraform | `terraform output order_service_url` | FAIL | exit code 126 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 8 | labs/lab05-iac-terraform | `curl $(terraform output -raw order_service_url)/health` | FAIL | exit code 3 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 9 | labs/lab05-iac-terraform | `curl -X POST $(terraform output -raw order_service_url)/orders \;   -H "Content-Type: application/json" \;   -d '{"item":"cappuccino","quantity":1,"price":4.5}'` | FAIL | exit code 3 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 10 | labs/lab05-iac-terraform | `terraform state list` | FAIL | exit code 126 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 11 | labs/lab05-iac-terraform | `terraform state show docker_container.order_service` | FAIL | exit code 126 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 12 | labs/lab05-iac-terraform | `terraform plan` | FAIL | exit code 126 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 13 | labs/lab05-iac-terraform | `terraform apply` | FAIL | exit code 126 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 14 | labs/lab05-iac-terraform | `terraform destroy` | FAIL | exit code 126 |
| | | | | | Output: `/bin/sh: /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/verify/bin/terraform: cannot execute bina` |
| lab05-iac-terraform | 15 | labs/lab05-iac-terraform | `docker ps -a --filter "name=tf-"` | PASS |  |
| lab06-kubernetes-kind | 1 | . | `kind create cluster --name devops-course` | PASS |  |
| lab06-kubernetes-kind | 2 | . | `kubectl get nodes` | PASS |  |
| lab06-kubernetes-kind | 3 | . | `kind load docker-image order-service:lab02 --name devops-course` | PASS |  |
| lab06-kubernetes-kind | 4 | . | `kind load docker-image payment-service:lab02 --name devops-course` | PASS |  |
| lab06-kubernetes-kind | 5 | labs/lab06-kubernetes-kind | `kubectl apply -k .` | PASS |  |
| lab06-kubernetes-kind | 6 | labs/lab06-kubernetes-kind | `kubectl get pods --watch` | SKIP | Classification: skip-watch |
| lab06-kubernetes-kind | 7 | labs/lab06-kubernetes-kind | `kubectl port-forward svc/order-service 8080:8000` | PASS | Background PID 111 |
| lab06-kubernetes-kind | 8 | labs/lab06-kubernetes-kind | `curl http://localhost:8080/health` | FAIL | exit code 7 |
| | | | | | Output: `% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current                                  Dload  Up` |
| lab06-kubernetes-kind | 9 | labs/lab06-kubernetes-kind | `curl -X POST http://localhost:8080/orders \;   -H "Content-Type: application/json" \;   -d '{"item":"espresso","quantity":2,"price":2.5}'` | FAIL | exit code 7 |
| | | | | | Output: `% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current                                  Dload  Up` |
| lab06-kubernetes-kind | 10 | labs/lab06-kubernetes-kind | `kubectl scale deployment order-service --replicas=3` | PASS |  |
| lab06-kubernetes-kind | 11 | labs/lab06-kubernetes-kind | `kubectl get pods -l app=order-service` | PASS |  |
| lab06-kubernetes-kind | 12 | labs/app | `docker build -t order-service:lab06 --build-arg BUILD_ID=lab06 -f Dockerfile .` | PASS |  |
| lab06-kubernetes-kind | 13 | labs/app | `kind load docker-image order-service:lab06 --name devops-course` | PASS |  |
| lab06-kubernetes-kind | 14 | labs/app | `kubectl set image deployment/order-service order=order-service:lab06` | PASS |  |
| lab06-kubernetes-kind | 15 | labs/app | `kubectl rollout status deployment/order-service` | PASS |  |
| lab06-kubernetes-kind | 16 | labs/app | `kubectl port-forward svc/order-service 8080:8000` | PASS | Background PID 205 |
| lab06-kubernetes-kind | 17 | labs/app | `curl http://localhost:8080/health` | PASS |  |
| lab06-kubernetes-kind | 18 | labs/app | `kubectl rollout history deployment/order-service` | PASS |  |
| lab06-kubernetes-kind | 19 | labs/app | `kubectl rollout undo deployment/order-service` | PASS |  |
| lab06-kubernetes-kind | 20 | labs/app | `kubectl rollout status deployment/order-service` | PASS |  |
| lab06-kubernetes-kind | 21 | labs/app | `kind delete cluster --name devops-course` | PASS |  |
| lab06-kubernetes-kind | 22 | labs/app | `kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml` | FAIL | exit code 1 |
| | | | | | Output: `Unable to connect to the server: dial tcp 54.232.119.62:443: i/o timeout` |
| lab07-devsecops | 1 | . | `brew install aquasecurity/trivy/trivy` | SKIP | Classification: skip-os-specific |
| lab07-devsecops | 2 | . | `winget install Aquasecurity.Trivy` | SKIP | Classification: skip-os-specific |
| lab07-devsecops | 3 | . | `curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin` | FAIL | exit code 71 |
| | | | | | Output: `aquasecurity/trivy info checking GitHub for latest tag aquasecurity/trivy info found version: 0.73.0 for v0.73.0/macOS/A` |
| lab07-devsecops | 4 | . | `trivy version` | SKIP | Trivy not installed |
| lab07-devsecops | 5 | . | `trivy image --severity HIGH,CRITICAL order-service:lab02` | SKIP | Trivy not installed |
| lab07-devsecops | 6 | . | `trivy fs --scanners secret .` | SKIP | Trivy not installed |
| lab07-devsecops | 7 | . | `trivy config labs/lab05-iac-terraform` | SKIP | Trivy not installed |
| lab07-devsecops | 8 | . | `trivy config labs/lab06-kubernetes-kind` | SKIP | Trivy not installed |
| lab07-devsecops | 9 | . | `brew install conftest   # macOS` | SKIP | Classification: skip-os-specific |
| lab07-devsecops | 10 | . | `mkdir -p labs/lab07-devsecops/policy` | PASS |  |
| lab07-devsecops | 11 | . | `cat > labs/lab07-devsecops/policy/labels.rego <<'EOF'; package main; deny[msg] {;   input.kind == "Deployment";   not input.metadata.labels.course;   msg := "Deployment must have a 'course' label"; }; EOF` | PASS |  |
| lab07-devsecops | 12 | . | `conftest test labs/lab06-kubernetes-kind/*.yaml --policy labs/lab07-devsecops/policy` | SKIP | Conftest not installed |
| lab07-devsecops | 13 | . | `git add labs/lab07-devsecops/policy` | FAIL | exit code 128 |
| | | | | | Output: `fatal: not a git repository (or any of the parent directories): .git` |
| lab07-devsecops | 14 | . | `git commit -m "Add Kubernetes label policy"` | FAIL | exit code 128 |
| | | | | | Output: `fatal: not a git repository (or any of the parent directories): .git` |
| lab08-observability | 1 | . | `docker compose -f docker-compose.observability.yml up -d --build` | FAIL | exit code 1 |
| | | | | | Output: `open /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/docker-compose.observability.yml: no such fil` |
| lab08-observability | 2 | . | `docker compose -f docker-compose.observability.yml ps` | FAIL | exit code 1 |
| | | | | | Output: `open /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/docker-compose.observability.yml: no such fil` |
| lab08-observability | 3 | . | `curl http://localhost:8080/metrics | grep order_requests_total` | FAIL | exit code 1 |
| | | | | | Output: `% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current                                  Dload  Up` |
| lab08-observability | 4 | . | `curl http://localhost:8001/metrics | grep payment_requests_total` | FAIL | exit code 1 |
| | | | | | Output: `% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current                                  Dload  Up` |
| lab08-observability | 5 | . | `for i in {1..30}; do` | FAIL | exit code 2 |
| | | | | | Output: `/bin/sh: -c: line 1: syntax error: unexpected end of file` |
| lab08-observability | 6 | . | `  curl -s -X POST http://localhost:8080/orders \;     -H "Content-Type: application/json" \;     -d '{"item":"mocha","quantity":1,"price":5.0}' > /dev/null` | FAIL | exit code 7 |
| lab08-observability | 7 | . | `done` | FAIL | exit code 2 |
| | | | | | Output: `/bin/sh: -c: line 0: syntax error near unexpected token `done' /bin/sh: -c: line 0: `done'` |
| lab08-observability | 8 | . | `docker compose -f docker-compose.observability.yml down --volumes` | FAIL | exit code 1 |
| | | | | | Output: `open /Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr/docker-compose.observability.yml: no such fil` |
| lab09-capstone | 1 | labs/lab09-capstone | `chmod +x run-capstone.sh` | PASS |  |
| lab09-capstone | 2 | labs/lab09-capstone | `./run-capstone.sh` | FAIL | exit code 1 |
| | | | | | Output: `=== Step 1: Run tests === Tests failed /opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest` |
| lab09-capstone | 3 | labs/lab09-capstone | `kubectl get all` | FAIL | exit code 1 |
| | | | | | Output: `E0812 14:24:34.760683     522 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: Get \"` |
| lab09-capstone | 4 | labs/lab09-capstone | `kubectl logs -l app=order-service --tail=20` | FAIL | exit code 1 |
| | | | | | Output: `E0812 14:24:34.931473     523 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: Get \"` |
| lab09-capstone | 5 | labs/lab09-capstone | `kubectl logs -l app=payment-service --tail=20` | FAIL | exit code 1 |
| | | | | | Output: `E0812 14:24:35.031554     525 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: Get \"` |

## Summary
- Total commands assessed: 161
- Passed: 59
- Failed: 69
- Skipped: 33