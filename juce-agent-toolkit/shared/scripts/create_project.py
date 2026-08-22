#!/usr/bin/env python3

import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

from find_starter_repo import locate


PLACEHOLDER_SUFFIXES = {".cpp", ".h", ".cmake", ".txt", ".md", ".env", ".example"}
EXCLUDES = {".git", "integrate", "todo"}


def generate_4letter_code(value: str) -> str:
    words = re.sub(r"[^a-zA-Z0-9 ]", "", value).split()
    if not words:
        return "XXXX"
    compact = "".join(words)
    if len(compact) <= 4:
        return compact.upper().ljust(4, "X")
    if len(words) >= 2:
        return (words[0][:2] + words[1][:2]).upper().ljust(4, "X")[:4]
    index = len(compact) // 2
    return f"{compact[0]}{compact[1]}{compact[index]}{compact[-1]}".upper()


def copytree(src: Path, dest: Path) -> None:
    def ignore(_dir: str, names: list[str]) -> set[str]:
        return {name for name in names if name in EXCLUDES}

    shutil.copytree(src, dest, ignore=ignore)


def replace_text(root: Path, replacements: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix
        if suffix not in PLACEHOLDER_SUFFIXES and not path.name.startswith(".env"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        for source, target in replacements.items():
            text = text.replace(source, target)
        if text != original:
            path.write_text(text, encoding="utf-8")


def write_env(path: Path, values: dict[str, str]) -> None:
    lines = [
        "# Project Configuration",
        f"PROJECT_NAME={values['PROJECT_NAME']}",
        f'PRODUCT_NAME="{values["PRODUCT_NAME"]}"',
        f"PROJECT_BUNDLE_ID={values['PROJECT_BUNDLE_ID']}",
        f'DEVELOPER_NAME="{values["DEVELOPER_NAME"]}"',
        "",
        "# JUCE Plugin Codes (4-letter identifiers)",
        f"PLUGIN_CODE={values['PLUGIN_CODE']}",
        f"PLUGIN_MANUFACTURER_CODE={values['PLUGIN_MANUFACTURER_CODE']}",
        "",
        f'PROJECT_PATH="{path.parent}"',
        "",
        "# Version Information",
        "VERSION_MAJOR=1",
        "VERSION_MINOR=0",
        "VERSION_PATCH=0",
        "VERSION_BUILD=1",
        "",
        "# Apple Developer Settings (for code signing/notarization)",
        f"APPLE_ID={values['APPLE_ID']}",
        f"TEAM_ID={values['TEAM_ID']}",
        f'APP_CERT="{values["APP_CERT"]}"',
        f'INSTALLER_CERT="{values["INSTALLER_CERT"]}"',
        f"APP_SPECIFIC_PASSWORD={values['APP_SPECIFIC_PASSWORD']}",
        "",
        "# GitHub Settings",
        f"GITHUB_USER={values['GITHUB_USER']}",
        f"GITHUB_REPO={values['GITHUB_REPO']}",
        "",
        "# DiagnosticKit Settings",
        f"ENABLE_DIAGNOSTICS={values['ENABLE_DIAGNOSTICS']}",
        "",
        "# Build Configuration",
        "CMAKE_BUILD_TYPE=Debug",
        "BUILD_DIR=build",
        "",
        "# JUCE Configuration",
        "JUCE_REPO=https://github.com/juce-framework/JUCE.git",
        "JUCE_BRANCH=master",
        "",
        "# GitHub Release Settings",
        "GITHUB_TOKEN=",
        "OPENROUTER_KEY_PRIVATE=",
        "OPENAI_API_KEY=",
        "RELEASE_NOTES_MODEL=openai/gpt-4o-mini",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def make_scripts_executable(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in {".sh", ".py"}:
            path.chmod(path.stat().st_mode | stat.S_IXUSR)


def init_git(root: Path, message: str) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True)


def maybe_create_github(root: Path, github_user: str, repo_name: str, public: bool) -> None:
    visibility = "--public" if public else "--private"
    subprocess.run(
        ["gh", "repo", "create", repo_name, visibility, "--description", f"{repo_name} - Audio Plugin built with JUCE"],
        cwd=root,
        check=True,
    )
    subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{github_user}/{repo_name}.git"], cwd=root, check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=root, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=root, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a JUCE starter project without the Claude plugin.")
    parser.add_argument("plugin_name")
    parser.add_argument("--starter")
    parser.add_argument("--clone-missing", help="Clone JUCE-Plugin-Starter here if missing")
    parser.add_argument("--destination-parent", default=".", help="Parent directory for the new project")
    parser.add_argument("--developer-name", default="")
    parser.add_argument("--bundle-id", default="")
    parser.add_argument("--github-user", default="")
    parser.add_argument("--apple-id", default="")
    parser.add_argument("--team-id", default="")
    parser.add_argument("--app-cert", default="")
    parser.add_argument("--installer-cert", default="")
    parser.add_argument("--app-specific-password", default="")
    parser.add_argument("--enable-diagnostics", action="store_true")
    parser.add_argument("--visage", action="store_true")
    parser.add_argument("--create-github", action="store_true")
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-init-git", action="store_true")
    args = parser.parse_args()

    starter = Path(args.starter).resolve() if args.starter else locate([])
    if not starter and args.clone_missing:
        subprocess.run(["python3", str(Path(__file__).with_name("find_starter_repo.py")), "--clone", args.clone_missing], check=True)
        starter = Path(args.clone_missing).resolve()
    if not starter:
        print("Could not locate JUCE-Plugin-Starter. Use --starter or --clone-missing.", file=sys.stderr)
        return 1

    plugin_name = args.plugin_name.strip()
    class_name = re.sub(r"[^a-zA-Z0-9]", "", plugin_name)
    if not class_name:
        print("Plugin name must contain at least one alphanumeric character.", file=sys.stderr)
        return 1
    project_folder = re.sub(r"[^a-zA-Z0-9]", "-", plugin_name).strip("-").lower()
    developer_name = args.developer_name or "Your Name"
    namespace = re.sub(r"[^a-zA-Z0-9]", "", developer_name).lower() or "audio"
    bundle_prefix = f"com.{re.sub(r'[^a-z0-9]', '', developer_name.lower())}" if developer_name != "Your Name" else "com.yourname"
    bundle_id = args.bundle_id or f"{bundle_prefix}.{project_folder}"
    plugin_code = generate_4letter_code(plugin_name)
    manufacturer_code = generate_4letter_code(developer_name)

    destination = Path(args.destination_parent).resolve() / project_folder
    if destination.exists():
        if not args.force:
            print(f"Destination already exists: {destination}. Use --force to overwrite.", file=sys.stderr)
            return 1
        shutil.rmtree(destination)

    copytree(starter, destination)
    replacements = {
        "PLUGIN_NAME_PLACEHOLDER": plugin_name,
        "CLASS_NAME_PLACEHOLDER": class_name,
        "PROJECT_FOLDER_PLACEHOLDER": project_folder,
        "BUNDLE_ID_PLACEHOLDER": bundle_id,
        "DEVELOPER_NAME_PLACEHOLDER": developer_name,
        "PLUGIN_MANUFACTURER_PLACEHOLDER": developer_name,
        "NAMESPACE_PLACEHOLDER": namespace,
        "PLUGIN_CODE_PLACEHOLDER": plugin_code,
        "PLUGIN_MANUFACTURER_CODE_PLACEHOLDER": manufacturer_code,
    }
    replace_text(destination, replacements)

    write_env(
        destination / ".env",
        {
            "PROJECT_NAME": class_name,
            "PRODUCT_NAME": plugin_name,
            "PROJECT_BUNDLE_ID": bundle_id,
            "DEVELOPER_NAME": developer_name,
            "PLUGIN_CODE": plugin_code,
            "PLUGIN_MANUFACTURER_CODE": manufacturer_code,
            "APPLE_ID": args.apple_id,
            "TEAM_ID": args.team_id,
            "APP_CERT": args.app_cert,
            "INSTALLER_CERT": args.installer_cert,
            "APP_SPECIFIC_PASSWORD": args.app_specific_password,
            "GITHUB_USER": args.github_user,
            "GITHUB_REPO": project_folder,
            "ENABLE_DIAGNOSTICS": "true" if args.enable_diagnostics else "false",
        },
    )
    make_scripts_executable(destination)

    if args.visage and (destination / "scripts" / "setup_visage.sh").exists():
        subprocess.run([str(destination / "scripts" / "setup_visage.sh")], cwd=destination, check=True)

    if not args.no_init_git:
        init_git(destination, f"Initial commit: {plugin_name} plugin from JUCE-Plugin-Starter template")

    if args.create_github and args.github_user:
        maybe_create_github(destination, args.github_user, project_folder, args.public)

    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
