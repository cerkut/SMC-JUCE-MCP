#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from pathlib import Path


TARGETS = {"all", "au", "auv3", "vst3", "clap", "standalone"}
ACTIONS = {"local", "test", "sign", "notarize", "pkg", "publish", "unsigned", "uninstall"}
REGEN_PATTERNS = (
    "CMakeLists.txt",
    ".env",
    ".env.ci",
    "Source/",
    "App/",
    "templates/",
    "external/visage",
)


def git_changed_files(root: Path) -> list[str]:
    files: list[str] = []
    for args in (["diff", "--name-only"], ["diff", "--name-only", "HEAD~1..HEAD"]):
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            files.extend(line.strip() for line in result.stdout.splitlines() if line.strip())
    return sorted(set(files))


def needs_regen(root: Path) -> bool:
    if not (root / "build").exists():
        return True
    for changed in git_changed_files(root):
        if any(changed == pattern or changed.startswith(pattern) for pattern in REGEN_PATTERNS):
            return True
    return False


def platform_name() -> str:
    if os.name == "nt":
        return "Windows"
    return subprocess.check_output(["uname", "-s"], text=True).strip()


def build_command(root: Path, tokens: list[str]) -> list[str]:
    if os.name == "nt":
        script = root / "scripts" / "build.ps1"
        if not script.exists():
            raise FileNotFoundError(f"Missing build script: {script}")
        return ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script), *tokens]

    script = root / "scripts" / "build.sh"
    if not script.exists():
        raise FileNotFoundError(f"Missing build script: {script}")
    return [str(script), *tokens]


def maybe_regenerate(root: Path, mode: str) -> None:
    if os.name == "nt":
        return
    if mode == "never":
        return
    if mode == "auto" and not needs_regen(root):
        return

    generator = root / "scripts" / "generate_and_open_xcode.sh"
    if generator.exists():
        subprocess.run([str(generator)], cwd=root, check=True)


def parse_tokens(tokens: list[str]) -> list[str]:
    parsed: list[str] = []
    targets = [token for token in tokens if token in TARGETS]
    actions = [token for token in tokens if token in ACTIONS]
    others = [token for token in tokens if token not in TARGETS and token not in ACTIONS]
    if not targets:
        targets = ["all"]
    parsed.extend(targets)
    if actions:
        parsed.append(actions[-1])
    parsed.extend(others)
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Portable wrapper for JUCE starter build and release workflows.")
    parser.add_argument("tokens", nargs="*", help="Targets, action, and passthrough options")
    parser.add_argument("--project-root", default=".", help="Project root")
    parser.add_argument("--regenerate", choices=["auto", "always", "never"], default="auto")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    tokens = parse_tokens(args.tokens)

    try:
        command = build_command(root, tokens)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not args.dry_run:
        maybe_regenerate(root, args.regenerate)

    print(f"Platform: {platform_name()}")
    print(f"Project root: {root}")
    print("Command:", " ".join(command))

    if args.dry_run:
        return 0

    result = subprocess.run(command, cwd=root, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
