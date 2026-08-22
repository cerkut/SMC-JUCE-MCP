---
name: juce-project-ops
description: "Guide portable project operations for JUCE-Plugin-Starter repos. Use when an agent needs the closest cross-host equivalent of `status`, `website`, or `vm`: inspecting project state, managing a portable VM registry, checking remote VM reachability, or maintaining a GitHub Pages download site and related release assets."
---

# JUCE Project Ops

Use this skill for the portable workflow behind `/juce-dev:status`, `/juce-dev:website`, and `/juce-dev:vm`.

## Status

Start with:
- `python3 ../../shared/scripts/inspect_juce_project.py`

That inspector is the toolkit's cross-host project status baseline. Use it before changing build, release, updater, or CI settings.

## VM Registry

Use the portable VM registry helper:
- `python3 ../../shared/scripts/vm_registry.py list`
- `python3 ../../shared/scripts/vm_registry.py add --name win --ssh-alias win-ssh --platform windows`
- `python3 ../../shared/scripts/vm_registry.py test`

The registry lives in:
- `.juce-agent-toolkit/vms.json`

This avoids depending on Claude-specific local metadata while still giving the project a repeatable VM inventory.

## Website

Prefer the project's own release asset and link-update scripts when they exist:
- `scripts/update_download_links.sh`

If the repo already has a `gh-pages` branch, treat website work as an update task. If not, create the page deliberately and confirm before publishing it.

## Guardrails

- Status is read-only by default.
- VM registry changes should be explicit and easy to review.
- Website publishing is public-facing; confirm before pushing generated page changes.
