#!/usr/bin/env python3
"""
Execute the command inventory produced by extract_lab_commands.py
and write a Markdown pass/fail report.
"""
import json
import os
import re
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_FILE = REPO_ROOT / "tools" / "lab_commands.json"
REPORT_FILE = REPO_ROOT / "lab-command-report.md"
BACKGROUND_PROCESSES = []
# Persist virtual-environment activation per directory across commands.
VENV_BY_DIR = {}
# Make host-downloaded course binaries available.
VERIFY_BIN = str(REPO_ROOT / "verify" / "bin")


def tool_available(name):
    return subprocess.run(
        f"command -v {name}", shell=True, capture_output=True
    ).returncode == 0


def run(cmd, cwd, classification):
    target = REPO_ROOT / cwd if cwd != "." else REPO_ROOT
    env = os.environ.copy()
    # Include downloaded binaries in PATH.
    env["PATH"] = VERIFY_BIN + ":" + env.get("PATH", "")

    # Remember when a command activates a venv so later commands use it.
    venv_match = None
    for pattern in (r"source\s+(\.venv[^\s;]+)/bin/activate",
                    r"\.\s+(\.venv[^\s;]+)/bin/activate"):
        m = re.search(pattern, cmd)
        if m:
            venv_match = m.group(1)
            break
    if venv_match:
        VENV_BY_DIR[str(target)] = venv_match
        # The activation itself is not a testable command.
        return "PASS", "venv activated", ""

    # Prepend the active venv to PATH for this command.
    active_venv = VENV_BY_DIR.get(str(target))
    if active_venv:
        env["PATH"] = str(target / active_venv / "bin") + ":" + env["PATH"]

    if classification in ("skip-os-specific", "skip-no-remote", "skip-tool-missing", "skip-watch"):
        return "SKIP", f"Classification: {classification}", ""

    # Auto-approve destructive Terraform commands so the runner does not hang.
    if cmd.strip().startswith("terraform destroy") and "-auto-approve" not in cmd:
        cmd = cmd.strip() + " -auto-approve"

    if classification == "conditional-tool":
        if "trivy" in cmd and not tool_available("trivy"):
            return "SKIP", "Trivy not installed", ""
        if "conftest" in cmd and not tool_available("conftest"):
            return "SKIP", "Conftest not installed", ""

    if classification == "background":
        proc = subprocess.Popen(
            cmd, shell=True, cwd=target,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True, env=env
        )
        BACKGROUND_PROCESSES.append(proc)
        time.sleep(2)
        return "PASS", f"Background PID {proc.pid}", ""

    # Run non-interactive docker exec
    if "docker exec -it" in cmd:
        cmd = cmd.replace("docker exec -it", "docker exec")

    try:
        result = subprocess.run(
            cmd, shell=True, cwd=target, capture_output=True, text=True,
            timeout=180, env=env
        )
    except subprocess.TimeoutExpired:
        return "FAIL", "Timeout (>180s)", ""
    except (FileNotFoundError, OSError) as exc:
        return "FAIL", f"Execution error: {exc}", ""

    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        return "PASS", "", output
    return "FAIL", f"exit code {result.returncode}", output


def main():
    inventory = json.loads(COMMANDS_FILE.read_text(encoding="utf-8"))

    lines = [
        "# Lab Command Verification Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}Z",
        "",
        "| Lab | # | Directory | Command | Status | Notes |",
        "|-----|---|-----------|---------|--------|-------|",
    ]

    total = passed = failed = skipped = 0
    for lab in sorted(inventory):
        print(f"\n=== {lab} ===", flush=True)
        for i, item in enumerate(inventory[lab]["commands"], 1):
            total += 1
            short = item["command"].replace("\n", "; ")[:80]
            print(f"[{i}] {short} ...", flush=True, end=" ")
            status, notes, output = run(
                item["command"], item["directory"], item["classification"]
            )
            print(status, flush=True)
            if status == "PASS":
                passed += 1
            elif status == "FAIL":
                failed += 1
            elif status == "SKIP":
                skipped += 1

            short_out = " ".join(output.splitlines()[:3])[:120]
            cmd_text = item["command"].replace("\n", "; ")
            lines.append(
                f"| {lab} | {i} | {item['directory']} | `{cmd_text}` | {status} | {notes} |"
            )
            if short_out and status == "FAIL":
                lines.append(f"| | | | | | Output: `{short_out}` |")

    lines += [
        "",
        "## Summary",
        f"- Total commands assessed: {total}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        f"- Skipped: {skipped}",
    ]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {REPORT_FILE}")


if __name__ == "__main__":
    try:
        main()
    finally:
        for proc in BACKGROUND_PROCESSES:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
