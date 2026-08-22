#!/usr/bin/env python3

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


TRUTHY = {"1", "true", "yes", "on"}


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def is_truthy(value: str | None) -> bool:
    return bool(value and value.strip().lower() in TRUTHY)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def parse_vm_notes(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- name:"):
            if current:
                entries.append(current)
            current = {"name": line.split(":", 1)[1].strip()}
        elif current and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip("- ").strip()] = value.strip()
    if current:
        entries.append(current)
    return entries


def detect_platforms(cmake_text: str, build_sh_text: str, build_ps1_exists: bool) -> list[str]:
    platforms: list[str] = []
    if "if(APPLE)" in cmake_text or "MACOSX_BUNDLE" in cmake_text or "generate_and_open_xcode.sh" in build_sh_text:
        platforms.append("macOS")
    if build_ps1_exists or "if(MSVC)" in cmake_text or "if(WIN32)" in cmake_text:
        platforms.append("Windows")
    if "UNIX AND NOT APPLE" in cmake_text or "BUILD_PLATFORM=\"Linux\"" in build_sh_text or "libwebkit2gtk" in build_sh_text:
        platforms.append("Linux")
    return platforms


def detect_ios(root: Path, cmake_text: str) -> bool:
    if "juce_add_gui_app" in cmake_text:
        return True
    app_dir = root / "App"
    if app_dir.exists() and any(app_dir.glob("Main*")):
        return True
    main_cpp = root / "Source" / "Main.cpp"
    if "START_JUCE_APPLICATION" in read_text(main_cpp):
        return True
    return False


def detect_website(root: Path) -> bool:
    local_branch = git_output(root, "branch", "--list", "gh-pages")
    remote_branch = git_output(root, "branch", "-r", "--list", "origin/gh-pages")
    return bool(local_branch or remote_branch)


def collect_summary(root: Path) -> dict[str, object]:
    env = parse_env_file(root / ".env")
    env_ci = parse_env_file(root / ".env.ci")
    cmake_text = read_text(root / "CMakeLists.txt")
    build_sh_text = read_text(root / "scripts" / "build.sh")
    build_ps1_exists = (root / "scripts" / "build.ps1").exists()

    vm_entries = parse_vm_notes(root / ".claude" / "juce-dev.local.md")
    toolkit_vm_file = root / ".juce-agent-toolkit" / "vms.json"
    if toolkit_vm_file.exists():
        try:
            toolkit_vms = json.loads(toolkit_vm_file.read_text(encoding="utf-8"))
            if isinstance(toolkit_vms, list):
                vm_entries.extend(item for item in toolkit_vms if isinstance(item, dict))
        except json.JSONDecodeError:
            pass

    scripts = {
        "build.sh": (root / "scripts" / "build.sh").exists(),
        "build.ps1": build_ps1_exists,
        "generate_and_open_xcode.sh": (root / "scripts" / "generate_and_open_xcode.sh").exists(),
        "setup_visage.sh": (root / "scripts" / "setup_visage.sh").exists(),
        "setup_sparkle.sh": (root / "scripts" / "setup_sparkle.sh").exists(),
        "setup_winsparkle.sh": (root / "scripts" / "setup_winsparkle.sh").exists(),
        "update_download_links.sh": (root / "scripts" / "update_download_links.sh").exists(),
        "export_signing_certs.sh": (root / "scripts" / "export_signing_certs.sh").exists(),
    }

    summary = {
        "path": str(root),
        "project_name": env.get("PROJECT_NAME") or root.name,
        "product_name": env.get("PRODUCT_NAME") or env.get("PROJECT_NAME") or root.name,
        "bundle_id": env.get("PROJECT_BUNDLE_ID", ""),
        "version": ".".join(
            [
                env.get("VERSION_MAJOR", "0"),
                env.get("VERSION_MINOR", "0"),
                env.get("VERSION_PATCH", "0"),
            ]
        ),
        "is_starter_project": all(
            [
                (root / ".env").exists(),
                (root / "CMakeLists.txt").exists(),
                scripts["build.sh"] or scripts["build.ps1"],
            ]
        ),
        "platforms": detect_platforms(cmake_text, build_sh_text, build_ps1_exists),
        "features": {
            "visage": is_truthy(env.get("USE_VISAGE_UI")) or (root / "external" / "visage").exists() or (root / "Source" / "Visage").exists(),
            "ios_app": detect_ios(root, cmake_text),
            "auto_updates": is_truthy(env.get("ENABLE_AUTO_UPDATE")) or (root / "Source" / "AutoUpdater.h").exists(),
            "diagnostics": is_truthy(env.get("ENABLE_DIAGNOSTICS")) or (root / "Tools" / "DiagnosticKit").exists(),
            "ci": (root / ".github" / "workflows" / "build.yml").exists(),
            "website": detect_website(root),
        },
        "scripts": scripts,
        "git": {
            "remote_origin": git_output(root, "remote", "get-url", "origin"),
            "branch": git_output(root, "branch", "--show-current"),
            "dirty": bool(git_output(root, "status", "--short")),
        },
        "env": {
            "developer_name": env.get("DEVELOPER_NAME", ""),
            "github_user": env.get("GITHUB_USER") or env.get("GITHUB_USERNAME", ""),
            "github_repo": env.get("GITHUB_REPO", ""),
            "ci_platforms": env.get("CI_PLATFORMS") or env_ci.get("CI_PLATFORMS", ""),
        },
        "vm_entries": vm_entries,
    }
    return summary


def render_text(summary: dict[str, object]) -> str:
    features = summary["features"]
    scripts = summary["scripts"]
    env = summary["env"]

    def yn(value: bool) -> str:
        return "yes" if value else "no"

    lines = [
        f"Project: {summary['product_name']} ({summary['project_name']})",
        f"Root: {summary['path']}",
        f"Starter project: {yn(bool(summary['is_starter_project']))}",
        f"Bundle ID: {summary['bundle_id'] or '(not set)'}",
        f"Version: {summary['version']}",
        f"Platforms: {', '.join(summary['platforms']) or '(unknown)'}",
        "",
        "Features:",
        f"  Visage UI: {yn(bool(features['visage']))}",
        f"  iOS app target: {yn(bool(features['ios_app']))}",
        f"  Auto-updates: {yn(bool(features['auto_updates']))}",
        f"  DiagnosticKit: {yn(bool(features['diagnostics']))}",
        f"  CI workflow: {yn(bool(features['ci']))}",
        f"  Website/gh-pages: {yn(bool(features['website']))}",
        "",
        "Scripts:",
        f"  build.sh: {yn(bool(scripts['build.sh']))}",
        f"  build.ps1: {yn(bool(scripts['build.ps1']))}",
        f"  generate_and_open_xcode.sh: {yn(bool(scripts['generate_and_open_xcode.sh']))}",
        f"  setup_visage.sh: {yn(bool(scripts['setup_visage.sh']))}",
        f"  setup_sparkle.sh: {yn(bool(scripts['setup_sparkle.sh']))}",
        f"  setup_winsparkle.sh: {yn(bool(scripts['setup_winsparkle.sh']))}",
        f"  update_download_links.sh: {yn(bool(scripts['update_download_links.sh']))}",
        f"  export_signing_certs.sh: {yn(bool(scripts['export_signing_certs.sh']))}",
        "",
        "Git:",
        f"  Branch: {summary['git']['branch'] or '(not on a branch)'}",
        f"  Origin: {summary['git']['remote_origin'] or '(no origin remote)'}",
        f"  Dirty: {yn(bool(summary['git']['dirty']))}",
        "",
        "Environment:",
        f"  Developer: {env['developer_name'] or '(not set)'}",
        f"  GitHub user: {env['github_user'] or '(not set)'}",
        f"  GitHub repo: {env['github_repo'] or '(not set)'}",
        f"  CI platforms: {env['ci_platforms'] or '(not set)'}",
        f"  VM entries: {len(summary['vm_entries'])}",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a JUCE-Plugin-Starter style project.")
    parser.add_argument("path", nargs="?", default=".", help="Project root to inspect")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Path not found: {root}", file=sys.stderr)
        return 1

    summary = collect_summary(root)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
