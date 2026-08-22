#!/usr/bin/env python3

import argparse
import os
import subprocess
from pathlib import Path


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def write_env(path: Path, values: dict[str, str]) -> None:
    existing = path.read_text(encoding="utf-8", errors="ignore").splitlines() if path.exists() else []
    updated_keys = set()
    lines = []
    for line in existing:
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            key = line.split("=", 1)[0].strip()
            if key in values:
                lines.append(f"{key}={values[key]}")
                updated_keys.add(key)
            else:
                lines.append(line)
        else:
            lines.append(line)
    for key, value in values.items():
        if key not in updated_keys:
            lines.append(f"{key}={value}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def default_branch(root: Path) -> str:
    result = subprocess.run(["git", "branch", "--show-current"], cwd=root, capture_output=True, text=True, check=False)
    branch = result.stdout.strip()
    return branch or "main"


def run_script(script: Path, root: Path) -> None:
    if script.suffix == ".py":
        subprocess.run(["python3", str(script)], cwd=root, check=True)
    else:
        subprocess.run([str(script)], cwd=root, check=True)


def ensure_appcast(path: Path, title: str, version: str) -> None:
    if path.exists():
        return
    contents = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
<rss version=\"2.0\">
  <channel>
    <title>{title}</title>
    <link></link>
    <description>Auto-update feed placeholder</description>
    <item>
      <title>Version {version}</title>
      <description>Initial appcast placeholder</description>
    </item>
  </channel>
</rss>
"""
    path.write_text(contents, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Portable updater setup wrapper for JUCE starter projects.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--platform", choices=["macos", "windows", "all"], default="all")
    parser.add_argument("--doctor", action="store_true")
    parser.add_argument("--generate-appcasts", action="store_true")
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    env_path = root / ".env"
    env = parse_env(env_path)

    github_user = env.get("GITHUB_USER", "")
    github_repo = env.get("GITHUB_REPO", "") or env.get("PROJECT_NAME", "")
    branch = default_branch(root)

    if args.platform in {"macos", "all"} and not args.skip_download:
        script = root / "scripts" / "setup_sparkle.sh"
        if not script.exists():
            script = Path(__file__).with_name("setup_sparkle.sh")
        run_script(script, root)

    if args.platform in {"windows", "all"} and not args.skip_download:
        script = root / "scripts" / "setup_winsparkle.sh"
        if not script.exists():
            script = Path(__file__).with_name("setup_winsparkle.sh")
        run_script(script, root)

    updates = {
        "ENABLE_AUTO_UPDATE": "TRUE",
        "AUTO_UPDATE_MODE": env.get("AUTO_UPDATE_MODE", "public"),
        "AUTO_UPDATE_EDDSA_PUBLIC_KEY": env.get("AUTO_UPDATE_EDDSA_PUBLIC_KEY", ""),
    }

    if github_user and github_repo:
        updates["AUTO_UPDATE_FEED_URL_MACOS"] = env.get(
            "AUTO_UPDATE_FEED_URL_MACOS",
            f"https://raw.githubusercontent.com/{github_user}/{github_repo}/{branch}/appcast-macos.xml",
        )
        updates["AUTO_UPDATE_FEED_URL_WINDOWS"] = env.get(
            "AUTO_UPDATE_FEED_URL_WINDOWS",
            f"https://raw.githubusercontent.com/{github_user}/{github_repo}/{branch}/appcast-windows.xml",
        )

    write_env(env_path, updates)

    if args.generate_appcasts:
        title = env.get("PRODUCT_NAME") or env.get("PROJECT_NAME") or root.name
        version = ".".join(
            [
                env.get("VERSION_MAJOR", "0"),
                env.get("VERSION_MINOR", "0"),
                env.get("VERSION_PATCH", "0"),
            ]
        )
        ensure_appcast(root / "appcast-macos.xml", f"{title} macOS Appcast", version)
        ensure_appcast(root / "appcast-windows.xml", f"{title} Windows Appcast", version)

    if args.doctor:
        subprocess.run(["python3", str(Path(__file__).with_name("auto_update_doctor.py")), str(root)], check=True)

    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
