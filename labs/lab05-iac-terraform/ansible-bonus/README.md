# Bonus — Configuration Management with Ansible (15 min)

Terraform and Ansible are both Infrastructure as Code, but they solve
different halves of the problem:

| | Terraform (Parts A–H) | Ansible (this bonus) |
|---|---|---|
| Job | **Provisioning** — create/destroy infrastructure | **Configuration** — packages, files, services on machines |
| Style | Declarative, state file tracks reality | Declarative tasks, idempotent modules, no state file |
| Typical unit | Provider + resource | Playbook + task |
| In this course | Docker network + containers | The Ubuntu VM itself |

## Run it

```bash
cd labs/lab05-iac-terraform/ansible-bonus
sudo apt-get install -y ansible   # once, if not already installed
ansible-playbook site.yml
```

Look at the recap line: some tasks report `changed`.

## The lesson: idempotence

Run it again:

```bash
ansible-playbook site.yml
```

This time the recap shows `changed=0` — Ansible checked the actual state and
found nothing to do. That is the same *converge to desired state* idea as
`terraform plan` showing "No changes".

Preview a change without applying it (like `terraform plan`):

```bash
ansible-playbook site.yml --check --diff
```

## Verify

```bash
cat /etc/motd
cat /etc/course-configured
htop --version
```
