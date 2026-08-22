#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path


TRUTHY = {"1", "true", "yes", "on"}


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


def is_truthy(value: str | None) -> bool:
    return bool(value and value.strip().lower() in TRUTHY)


def has_xml_tags(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return "<rss" in text and "<channel" in text


def add_check(checks: list[dict[str, str]], name: str, ok: bool, details: str, level: str | None = None) -> None:
    checks.append(
        {
            "name": name,
            "status": level or ("pass" if ok else "fail"),
            "details": details,
        }
    )


def run_checks(root: Path) -> dict[str, object]:
    env = parse_env(root / ".env")
    version = ".".join(
        [
            env.get("VERSION_MAJOR", "0"),
            env.get("VERSION_MINOR", "0"),
            env.get("VERSION_PATCH", "0"),
        ]
    )

    checks: list[dict[str, str]] = []

    add_check(checks, ".env present", (root / ".env").exists(), str(root / ".env"))
    add_check(
        checks,
        "Auto-update enabled",
        is_truthy(env.get("ENABLE_AUTO_UPDATE")),
        "ENABLE_AUTO_UPDATE should be TRUE to ship updater support",
        "pass" if is_truthy(env.get("ENABLE_AUTO_UPDATE")) else "warn",
    )
    add_check(
        checks,
        "Public EdDSA key configured",
        bool(env.get("AUTO_UPDATE_EDDSA_PUBLIC_KEY")),
        "AUTO_UPDATE_EDDSA_PUBLIC_KEY should be set in .env",
        "pass" if env.get("AUTO_UPDATE_EDDSA_PUBLIC_KEY") else "warn",
    )
    add_check(
        checks,
        "Update mode configured",
        bool(env.get("AUTO_UPDATE_MODE")),
        "AUTO_UPDATE_MODE should usually be set to public",
        "pass" if env.get("AUTO_UPDATE_MODE") else "warn",
    )
    add_check(
        checks,
        "GitHub repo configured",
        bool(env.get("GITHUB_USER") and env.get("GITHUB_REPO")),
        "GITHUB_USER and GITHUB_REPO are required for release feeds",
        "pass" if env.get("GITHUB_USER") and env.get("GITHUB_REPO") else "warn",
    )

    add_check(
        checks,
        "Source/AutoUpdater.h",
        (root / "Source" / "AutoUpdater.h").exists(),
        "Shared updater header",
    )
    add_check(
        checks,
        "Source/StandaloneApp.cpp",
        (root / "Source" / "StandaloneApp.cpp").exists(),
        "Standalone app entry point used by updater menu wiring",
    )
    add_check(
        checks,
        "Source/AutoUpdater_Mac.mm",
        (root / "Source" / "AutoUpdater_Mac.mm").exists(),
        "macOS Sparkle implementation",
        "pass" if (root / "Source" / "AutoUpdater_Mac.mm").exists() else "warn",
    )
    add_check(
        checks,
        "Source/AutoUpdater_Win.cpp",
        (root / "Source" / "AutoUpdater_Win.cpp").exists(),
        "Windows WinSparkle implementation",
        "pass" if (root / "Source" / "AutoUpdater_Win.cpp").exists() else "warn",
    )

    add_check(
        checks,
        "Sparkle framework",
        (root / "external" / "Sparkle.framework").exists(),
        "external/Sparkle.framework",
        "pass" if (root / "external" / "Sparkle.framework").exists() else "warn",
    )
    add_check(
        checks,
        "Sparkle sign_update tool",
        (root / "external" / "bin" / "sign_update").exists(),
        "external/bin/sign_update",
        "pass" if (root / "external" / "bin" / "sign_update").exists() else "warn",
    )
    add_check(
        checks,
        "Sparkle generate_keys tool",
        (root / "external" / "bin" / "generate_keys").exists(),
        "external/bin/generate_keys",
        "pass" if (root / "external" / "bin" / "generate_keys").exists() else "warn",
    )
    add_check(
        checks,
        "WinSparkle headers",
        (root / "external" / "WinSparkle" / "include" / "winsparkle.h").exists(),
        "external/WinSparkle/include/winsparkle.h",
        "pass" if (root / "external" / "WinSparkle" / "include" / "winsparkle.h").exists() else "warn",
    )
    add_check(
        checks,
        "WinSparkle x64 library",
        (root / "external" / "WinSparkle" / "x64" / "WinSparkle.lib").exists(),
        "external/WinSparkle/x64/WinSparkle.lib",
        "pass" if (root / "external" / "WinSparkle" / "x64" / "WinSparkle.lib").exists() else "warn",
    )
    add_check(
        checks,
        "WinSparkle tool",
        (root / "external" / "WinSparkle" / "bin" / "winsparkle-tool.exe").exists(),
        "external/WinSparkle/bin/winsparkle-tool.exe",
        "pass" if (root / "external" / "WinSparkle" / "bin" / "winsparkle-tool.exe").exists() else "warn",
    )

    cmake_text = (root / "CMakeLists.txt").read_text(encoding="utf-8", errors="ignore") if (root / "CMakeLists.txt").exists() else ""
    add_check(
        checks,
        "CMake auto-update wiring",
        "ENABLE_AUTO_UPDATE" in cmake_text,
        "CMakeLists.txt should contain updater wiring",
        "pass" if "ENABLE_AUTO_UPDATE" in cmake_text else "warn",
    )

    mac_feed = env.get("AUTO_UPDATE_FEED_URL_MACOS", "")
    win_feed = env.get("AUTO_UPDATE_FEED_URL_WINDOWS", "")
    add_check(
        checks,
        "macOS feed URL",
        bool(mac_feed),
        mac_feed or "AUTO_UPDATE_FEED_URL_MACOS is missing",
        "pass" if mac_feed else "warn",
    )
    add_check(
        checks,
        "Windows feed URL",
        bool(win_feed),
        win_feed or "AUTO_UPDATE_FEED_URL_WINDOWS is missing",
        "pass" if win_feed else "warn",
    )

    mac_appcast = root / "appcast-macos.xml"
    win_appcast = root / "appcast-windows.xml"
    add_check(
        checks,
        "macOS appcast XML",
        mac_appcast.exists() and has_xml_tags(mac_appcast),
        str(mac_appcast),
        "pass" if mac_appcast.exists() and has_xml_tags(mac_appcast) else "warn",
    )
    add_check(
        checks,
        "Windows appcast XML",
        win_appcast.exists() and has_xml_tags(win_appcast),
        str(win_appcast),
        "pass" if win_appcast.exists() and has_xml_tags(win_appcast) else "warn",
    )
    if mac_appcast.exists():
        add_check(
            checks,
            "macOS appcast mentions current version",
            version in mac_appcast.read_text(encoding="utf-8", errors="ignore"),
            f"Expected version {version} in {mac_appcast.name}",
            "pass" if version in mac_appcast.read_text(encoding="utf-8", errors="ignore") else "warn",
        )
    if win_appcast.exists():
        add_check(
            checks,
            "Windows appcast mentions current version",
            version in win_appcast.read_text(encoding="utf-8", errors="ignore"),
            f"Expected version {version} in {win_appcast.name}",
            "pass" if version in win_appcast.read_text(encoding="utf-8", errors="ignore") else "warn",
        )

    counts = {
        "pass": sum(1 for check in checks if check["status"] == "pass"),
        "warn": sum(1 for check in checks if check["status"] == "warn"),
        "fail": sum(1 for check in checks if check["status"] == "fail"),
    }
    return {"path": str(root), "version": version, "checks": checks, "counts": counts}


def render_text(report: dict[str, object]) -> str:
    lines = [f"Auto-update doctor for {report['path']}", f"Version: {report['version']}", ""]
    for check in report["checks"]:
        marker = {
            "pass": "PASS",
            "warn": "WARN",
            "fail": "FAIL",
        }[check["status"]]
        lines.append(f"[{marker}] {check['name']}: {check['details']}")
    lines.append("")
    lines.append(
        "Summary: "
        f"{report['counts']['pass']} pass, "
        f"{report['counts']['warn']} warn, "
        f"{report['counts']['fail']} fail"
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate JUCE starter auto-update setup.")
    parser.add_argument("path", nargs="?", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Path not found: {root}", file=sys.stderr)
        return 1

    report = run_checks(root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
