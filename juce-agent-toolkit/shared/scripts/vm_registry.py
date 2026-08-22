#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from pathlib import Path


def registry_path(root: Path) -> Path:
    return root / ".juce-agent-toolkit" / "vms.json"


def load_registry(root: Path) -> list[dict[str, str]]:
    path = registry_path(root)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return [entry for entry in data if isinstance(entry, dict)]
    return []


def save_registry(root: Path, entries: list[dict[str, str]]) -> None:
    path = registry_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_vm(entry: dict[str, str]) -> dict[str, str]:
    alias = entry["ssh_alias"]
    command = "uname -s || cmd /c ver"
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", alias, command],
        capture_output=True,
        text=True,
        check=False,
    )
    status = "online" if result.returncode == 0 else "offline"
    details = result.stdout.strip() or result.stderr.strip()
    return {"status": status, "details": details}


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage a portable JUCE Agent Toolkit VM registry.")
    parser.add_argument("command", choices=["list", "add", "remove", "test"])
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--name")
    parser.add_argument("--ssh-alias")
    parser.add_argument("--platform")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    entries = load_registry(root)

    if args.command == "add":
        if not args.name or not args.ssh_alias or not args.platform:
            parser.error("add requires --name, --ssh-alias, and --platform")
        entries = [entry for entry in entries if entry.get("name") != args.name]
        entries.append(
            {
                "name": args.name,
                "platform": args.platform,
                "project_dir": args.project_dir,
                "ssh_alias": args.ssh_alias,
            }
        )
        save_registry(root, entries)
        result: object = entries
    elif args.command == "remove":
        if not args.name:
            parser.error("remove requires --name")
        entries = [entry for entry in entries if entry.get("name") != args.name]
        save_registry(root, entries)
        result = entries
    elif args.command == "test":
        if args.name:
            selected = [entry for entry in entries if entry.get("name") == args.name]
        else:
            selected = entries
        result = []
        for entry in selected:
            report = dict(entry)
            report.update(test_vm(entry))
            result.append(report)
    else:
        result = entries

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if isinstance(result, list):
            if not result:
                print("No VM entries found")
            for entry in result:
                line = f"{entry.get('name', '(unnamed)')} [{entry.get('platform', 'unknown')}] -> {entry.get('ssh_alias', '')}"
                if entry.get("project_dir"):
                    line += f" ({entry['project_dir']})"
                if entry.get("status"):
                    line += f" :: {entry['status']}"
                print(line)
                if entry.get("details"):
                    print(f"  {entry['details']}")
        else:
            print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
