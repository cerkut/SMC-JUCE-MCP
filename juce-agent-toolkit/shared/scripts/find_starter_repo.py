#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_CANDIDATES = [
    Path.cwd() / "JUCE-Plugin-Starter",
    Path.home() / "Code" / "JUCE-Plugin-Starter",
    Path.home() / "Developer" / "JUCE-Plugin-Starter",
    Path.home() / "src" / "JUCE-Plugin-Starter",
]


def looks_like_starter(path: Path) -> bool:
    return (
        path.exists()
        and (path / "scripts" / "init_plugin_project.sh").exists()
        and (path / ".env.example").exists()
        and (path / "CMakeLists.txt").exists()
    )


def locate(extra: list[Path]) -> Path | None:
    env_path = os.environ.get("JUCE_PLUGIN_STARTER_PATH")
    candidates = []
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend(extra)
    candidates.extend(DEFAULT_CANDIDATES)
    for candidate in candidates:
        if looks_like_starter(candidate.expanduser().resolve()):
            return candidate.expanduser().resolve()
    return None


def clone_repo(dest: Path) -> Path:
    dest = dest.expanduser().resolve()
    if dest.exists() and any(dest.iterdir()):
        raise RuntimeError(f"Destination already exists and is not empty: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "https://github.com/danielraffel/JUCE-Plugin-Starter", str(dest)],
        check=True,
    )
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description="Locate or optionally clone JUCE-Plugin-Starter.")
    parser.add_argument("--candidate", action="append", default=[], help="Additional candidate path")
    parser.add_argument("--clone", help="Clone the starter repo here if not found")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    extra = [Path(item) for item in args.candidate]
    found = locate(extra)
    cloned = False

    if not found and args.clone:
        found = clone_repo(Path(args.clone))
        cloned = True

    if args.json:
        print(
            json.dumps(
                {
                    "found": str(found) if found else "",
                    "cloned": cloned,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        if found:
            prefix = "Cloned" if cloned else "Found"
            print(f"{prefix}: {found}")
        else:
            print("Not found", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
