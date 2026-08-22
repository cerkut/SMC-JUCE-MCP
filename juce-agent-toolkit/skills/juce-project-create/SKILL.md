---
name: juce-project-create
description: "Guide portable creation of a new JUCE plugin project from JUCE-Plugin-Starter. Use when an agent needs the closest cross-host equivalent of `/juce-dev:create`: locating or cloning the starter template, collecting project and signing settings, running `init_plugin_project.sh`, and handing off to follow-up setup skills such as Visage or auto-updates."
---

# JUCE Project Create

Use this skill for the portable workflow behind `/juce-dev:create`.

## Start Here

1. Locate the starter repo:
   - `python3 ../../shared/scripts/find_starter_repo.py`
2. Use the portable wrapper if you want the toolkit to do the starter copy and placeholder replacement:
   - `python3 ../../shared/scripts/create_project.py "My Plugin"`
2. If it is not present, clone it:
   - `python3 ../../shared/scripts/find_starter_repo.py --clone ~/Code/JUCE-Plugin-Starter`
3. Confirm the user wants:
   - plugin name
   - optional Visage UI
   - optional GitHub repo creation
   - signing or developer identity values reused from the starter `.env`

## Preferred Workflow

1. Use the starter repo's own `scripts/init_plugin_project.sh`.
2. Or use `../../shared/scripts/create_project.py` when you want a cross-host wrapper around the same starter conventions.
2. Reuse configured developer values from the starter `.env` when they are already real and not placeholders.
3. Let the starter script perform placeholder replacement and project initialization.
4. After creation:
   - use `juce-setup-visage` if the project should start with Visage
   - use `juce-build-release` for the first build
   - use `juce-auto-updates` if updater support is needed

## Practical Limits

This is not as guided as the Claude plugin:
- no slash-command menu
- no built-in AskUserQuestion flow
- no plugin-managed GitHub bootstrap

But it does give the agent a portable path to either the real starter creation script or the toolkit wrapper instead of leaving project creation entirely manual.

## Guardrails

- Prefer the starter repo's own creation script over recreating placeholder logic in the toolkit.
- Do not claim feature parity with the plugin's full interactive wizard.
- If the user wants a non-starter project, say so clearly and stop using this skill.
