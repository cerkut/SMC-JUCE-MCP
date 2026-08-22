#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path


EXCLUDES = {".git", "build", "build-debug", "build-release", "external", ".juce_cache"}

PATTERNS = {
    "macos": [
        (re.compile(r"\.mm$"), "Objective-C++ source files need Apple-only guards"),
        (re.compile(r"JUCE_MAC|if\(APPLE\)|MACOSX_BUNDLE"), "macOS-specific compile or CMake guards"),
        (re.compile(r"AudioUnit|AUv3|Sparkle|codesign|notarytool|xcrun"), "macOS-specific plugin or signing flow"),
    ],
    "windows": [
        (re.compile(r"JUCE_WINDOWS|if\(WIN32\)|if\(MSVC\)|\.lib\b"), "Windows-specific guards or libraries"),
        (re.compile(r"WinSparkle|Inno Setup|Setup\.exe|signtool"), "Windows-specific update or installer flow"),
    ],
    "linux": [
        (re.compile(r"JUCE_LINUX|UNIX AND NOT APPLE|pkg-config|webkit2gtk"), "Linux-specific guards or dependencies"),
        (re.compile(r"\.so\b|apt install|tar\.gz"), "Linux packaging or dependency flow"),
    ],
}


def scan_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in EXCLUDES for part in path.parts):
            continue
        if path.is_file() and path.suffix in {".cpp", ".cc", ".c", ".h", ".hpp", ".mm", ".m", ".txt", ".cmake", ".sh", ".ps1"}:
            files.append(path)
    return files


def audit(root: Path, target: str) -> dict[str, object]:
    files = scan_files(root)
    issues: list[dict[str, str]] = []
    portable: list[str] = []

    cmake = root / "CMakeLists.txt"
    build_sh = root / "scripts" / "build.sh"
    build_ps1 = root / "scripts" / "build.ps1"

    if (root / "external" / "visage").exists():
        portable.append("Visage dependency is present; treat it as portable unless platform-specific patches disagree.")

    if target in {"windows", "all"} and not build_ps1.exists():
        issues.append({"path": "scripts/build.ps1", "reason": "Windows target expects a PowerShell build entrypoint."})
    if target in {"linux", "all"} and not build_sh.exists():
        issues.append({"path": "scripts/build.sh", "reason": "Linux target expects a shell build entrypoint."})
    if target in {"macos", "all"} and not (root / "scripts" / "generate_and_open_xcode.sh").exists():
        issues.append({"path": "scripts/generate_and_open_xcode.sh", "reason": "macOS starter projects usually keep an Xcode generation script."})

    target_patterns = [target] if target != "all" else ["macos", "windows", "linux"]
    for file_path in files:
        rel = file_path.relative_to(root)
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for platform in target_patterns:
            for pattern, reason in PATTERNS[platform]:
                if pattern.search(str(rel)) or pattern.search(text):
                    issues.append({"path": str(rel), "reason": reason})

    unique_issues: list[dict[str, str]] = []
    seen = set()
    for issue in issues:
        key = (issue["path"], issue["reason"])
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    return {
        "path": str(root),
        "target": target,
        "issue_count": len(unique_issues),
        "issues": unique_issues,
        "portable": portable,
        "recommendations": [
            "Guard platform-specific plugin formats in CMake.",
            "Keep update frameworks behind platform checks.",
            "Validate the target platform with a real build after code changes.",
        ],
    }


def render_text(report: dict[str, object]) -> str:
    lines = [f"Port audit for {report['path']} -> {report['target']}", ""]
    if report["portable"]:
        lines.append("Portable signals:")
        for item in report["portable"]:
            lines.append(f"- {item}")
        lines.append("")
    if report["issues"]:
        lines.append("Issues:")
        for issue in report["issues"]:
            lines.append(f"- {issue['path']}: {issue['reason']}")
    else:
        lines.append("No obvious platform-specific issues found.")
    lines.append("")
    lines.append("Recommendations:")
    for item in report["recommendations"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a lightweight cross-platform JUCE port audit.")
    parser.add_argument("target", choices=["macos", "windows", "linux", "all"])
    parser.add_argument("path", nargs="?", default=".", help="Project root")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    report = audit(root, args.target)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
