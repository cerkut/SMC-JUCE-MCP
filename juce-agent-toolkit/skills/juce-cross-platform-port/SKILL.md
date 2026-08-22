---
name: juce-cross-platform-port
description: "Guide portable cross-platform audits and porting work for JUCE plugin repos. Use when an agent needs the closest cross-host equivalent of `/juce-dev:port`: scanning for platform-specific code, identifying missing build or updater support, planning Windows or Linux work from a macOS-first repo, or validating a port with real target-specific follow-up steps."
---

# JUCE Cross-Platform Port

Use this skill for the portable workflow behind `/juce-dev:port`.

## Start Here

1. Run the lightweight audit:
   - `python3 ../../shared/scripts/port_audit.py windows`
   - `python3 ../../shared/scripts/port_audit.py linux`
   - `python3 ../../shared/scripts/port_audit.py macos`
2. Inspect the project state:
   - `python3 ../../shared/scripts/inspect_juce_project.py`
3. If the project uses remote test VMs, check them with:
   - `python3 ../../shared/scripts/vm_registry.py test`

## Workflow

1. Treat the audit as a triage pass, not the final answer.
2. Prioritize:
   - CMake platform guards
   - build entrypoints
   - platform-specific updater or installer code
   - source files that assume one platform
3. After code changes, validate on the real target platform or through CI.

## Guardrails

- Do not claim the audit is exhaustive. It is a lightweight scanner.
- Visage should be treated as portable by default unless the actual bridge code is platform-bound.
- Keep the port plan explicit: audit, change, build, test.
