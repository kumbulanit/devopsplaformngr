#!/usr/bin/env python3
"""
Extract runnable shell commands from labs/*/README.md into tools/lab_commands.json.
Run from the repository root.
"""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LABS_DIR = REPO_ROOT / "labs"
OUTPUT = REPO_ROOT / "tools" / "lab_commands.json"

SKIP_LINE_PATTERNS = [
    r"^\s*#.*Expected:",
    r"^\s*#.*Windows:",
    r"^\s*#.*Inside the container:",
    r"^\s*#.*Press Ctrl\+C",
    r"^\s*#.*In Prometheus UI:",
    r"^\s*#.*Open http",
    r"^\s*#.*Example:",
    r"^\s*#.*Note:",
]

SKIP_CMD_PREFIXES = [
    "brew ", "winget ", "choco ",
    "sudo apt-get ", "sudo systemctl ", "sudo usermod ",
    "sudo install ", "sudo mv ", "sudo gpg ",
    "dpkg ", "rm kubectl",
    "curl -Lo ./kind", "curl -LO ", "curl -fsSL https://apt.releases.hashicorp.com",
    "echo \"deb [signed-by=",
    "open http", "xdg-open ",
]


def extract_bash_blocks(text):
    return re.findall(r"```(?:bash|shell|sh)\n(.*?)```", text, re.DOTALL)


def split_commands(block):
    lines = block.splitlines()
    commands, current = [], []
    in_heredoc, heredoc_delim = False, None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if any(re.match(p, line) for p in SKIP_LINE_PATTERNS):
            continue

        if in_heredoc:
            current.append(line)
            if stripped == heredoc_delim:
                in_heredoc = False
                heredoc_delim = None
                commands.append("\n".join(current))
                current = []
            continue

        heredoc_match = re.search(r"<<\s*['\"]?(?P<delim>\w+)['\"]?", line)
        if heredoc_match:
            in_heredoc = True
            heredoc_delim = heredoc_match.group("delim")
            current.append(line)
            continue

        current.append(line)
        if not line.rstrip().endswith("\\"):
            commands.append("\n".join(current))
            current = []

    if current:
        commands.append("\n".join(current))
    return commands


def normalize_path(path_str):
    """Replace README placeholder paths with real repo paths."""
    placeholder = "/path/to/labs/app"
    if placeholder in path_str:
        return path_str.replace(placeholder, str(REPO_ROOT / "labs" / "app"))
    return path_str


def classify(cmd):
    first = cmd.splitlines()[0].strip()
    if any(first.startswith(p) for p in SKIP_CMD_PREFIXES):
        return "skip-os-specific"
    if first.startswith("git push origin"):
        return "skip-no-remote"
    if first.startswith("act "):
        return "skip-tool-missing"
    if "trivy " in first or "conftest " in first:
        return "conditional-tool"
    if first.startswith(("uvicorn ", "kubectl port-forward ")):
        return "background"
    if "--watch" in cmd:
        return "skip-watch"
    if "docker exec -it" in first:
        return "interactive-exec"
    return "run"


def main():
    inventory = {}
    for lab_dir in sorted(LABS_DIR.iterdir()):
        if not lab_dir.is_dir() or not lab_dir.name.startswith("lab"):
            continue
        readme = lab_dir / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text(encoding="utf-8")
        commands = []
        cwd = "."
        for block in extract_bash_blocks(text):
            for cmd in split_commands(block):
                m = re.match(r"^cd\s+(\S+)(?:\s*&&\s*)?", cmd.strip())
                if m:
                    cwd = normalize_path(m.group(1))
                    cmd = re.sub(r"^cd\s+\S+(?:\s*&&\s*)?", "", cmd.strip()).strip()
                    if not cmd:
                        continue
                commands.append({
                    "command": normalize_path(cmd),
                    "directory": cwd,
                    "classification": classify(cmd),
                })
        inventory[lab_dir.name] = {
            "title": text.splitlines()[0].lstrip("# ").strip(),
            "commands": commands,
        }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    total = sum(len(v["commands"]) for v in inventory.values())
    print(f"Wrote {len(inventory)} labs, {total} commands to {OUTPUT}")


if __name__ == "__main__":
    main()
