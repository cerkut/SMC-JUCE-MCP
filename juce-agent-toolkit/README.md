# JUCE Agent Toolkit

Portable JUCE workflow skills for coding agents outside Claude Code.

JUCE Agent Toolkit gives agents like Codex, Cursor, OpenCode, Gemini CLI, GitHub Copilot, and other supported hosts practical help with the custom workflow around your JUCE ecosystem:

- `JUCE-Plugin-Starter` project setup and conventions
- `.env`, build, signing, and release flows
- Visage GPU UI setup and debugging
- cross-DAW plugin behavior that is easy to get wrong without project context

This is not a general JUCE API docs package, and it is not a clone of the `juce-dev` Claude Code plugin.

## Installing JUCE Agent Toolkit

You can install these skills into Codex, Gemini CLI, Cursor, GitHub Copilot, OpenCode, and other supported hosts by using `npx`:

```bash
npx skills add https://github.com/danielraffel/juce-agent-toolkit --skill '*'
```

If you get the error `npx: command not found`, you need to [install Node first](https://nodejs.org/en/download). On macOS, the quickest route is:

```bash
brew install node
```

When using `npx`, the installer will guide you through which agents to install into and whether the toolkit should be installed for just the current project or for all your projects.

If you prefer, you can also clone this repository and install it however you want.

## What You Get

- `juce-project-starter`: starter template structure, `.env` setup, formats, placeholder replacement, and MIDI generator patterns
- `juce-visage-ui`: JUCE + Visage UI integration and debugging on macOS and iOS
- `juce-project-create`: portable project creation flow using JUCE-Plugin-Starter
- `juce-build-release`: build, test, sign, package, and publish workflows based on starter scripts
- `juce-setup-visage`: portable setup flow for adding Visage to an existing starter project
- `juce-setup-ios`: portable setup flow for adding or repairing an iOS app target
- `juce-auto-updates`: Sparkle and WinSparkle setup plus updater doctor guidance
- `juce-ci-release`: CI, release-notes, and signing-secret workflow guidance
- `juce-project-ops`: status, website, and VM operations
- `juce-cross-platform-port`: lightweight port audit and planning support
- `shared/scripts/inspect_juce_project.py`: reusable project inspector used by the workflow skills
- `shared/scripts/auto_update_doctor.py`: repeatable updater validation pass
- `shared/scripts/build_release.py`: portable wrapper for starter build and publish flows
- `shared/scripts/create_project.py`: portable starter-based project creation wrapper
- `shared/scripts/setup_sparkle.sh` and `shared/scripts/setup_winsparkle.sh`: portable updater download helpers
- `shared/scripts/setup_updates.py`: portable updater setup wrapper
- `shared/scripts/find_starter_repo.py`: locates or clones JUCE-Plugin-Starter
- `shared/scripts/vm_registry.py`: portable VM registry for non-Claude hosts
- `shared/scripts/port_audit.py`: lightweight cross-platform audit helper
- `shared/scripts/bump_version.py` and `shared/scripts/generate_release_notes.py`: portable release helpers

In plain English:

- this helps an agent understand your starter-based project faster
- this helps an agent run more of the build and setup workflow without guessing
- this helps an agent debug Visage-based plugin UIs without guessing
- this still does not recreate Claude Code slash commands or menu-driven prompts

## Parity Matrix

Matrix key:

- `Yes`: strong toolkit support today
- `Partial`: meaningful skill or script support, but not full plugin automation
- `No`: plugin-only today

This matrix is the release-by-release parity tracker for the toolkit.

| Capability | JUCE Agent Toolkit v5.0 | `juce-dev` Claude Code plugin |
|---|---|---|
| Understand JUCE-Plugin-Starter conventions | Yes | Yes |
| Understand JUCE + Visage UI patterns | Yes | Yes |
| Build, test, sign, package, and publish from starter scripts | Yes | Yes |
| Add Visage to an existing starter project | Partial | Yes |
| Add an iOS app target | Partial | Yes |
| Add auto-update support | Partial | Yes |
| Create a new project from the starter | Yes | Yes |
| Inspect project status and enabled features | Yes | Yes |
| Trigger CI, view logs, and manage release secrets | Partial | Yes |
| Create or refresh a GitHub Pages download site | Partial | Yes |
| Manage cross-platform VMs | Partial | Yes |
| Audit and port a project across macOS, Windows, and Linux | Partial | Yes |
| Works in Codex, Cursor, OpenCode, Gemini CLI, and similar hosts | Yes | No |

The easiest way to think about it is:

- JUCE Agent Toolkit is the portable skills-and-scripts layer
- `juce-dev` is the best Claude Code automation layer on top

If you want the full guided workflow in Claude Code, use the plugin:

- https://www.generouscorp.com/generous-corp-marketplace/plugins/juce-dev/

If you already use `juce-dev`, do not install overlapping toolkit skills into Claude Code. Use this toolkit for your other agents instead.

If you want official JUCE class and method documentation inside your agent, use the JUCE docs MCP server alongside this toolkit:

- https://github.com/danielraffel/juce-docs-mcp-server

## Using JUCE Agent Toolkit

These are skills, not slash commands.

In hosts that support explicit skill invocation, use the host's normal skill shortcut with one of these names:

- `juce-project-starter`
- `juce-visage-ui`
- `juce-project-create`
- `juce-build-release`
- `juce-setup-visage`
- `juce-setup-ios`
- `juce-auto-updates`
- `juce-ci-release`
- `juce-project-ops`
- `juce-cross-platform-port`

You can also trigger the skills using natural language. For example:

```text
Use the juce-project-create skill to bootstrap a new project from JUCE-Plugin-Starter.
Use the juce-build-release skill to help me run a signed VST3 build from this starter project.
Use the juce-setup-visage skill to add Visage to this existing JUCE-Plugin-Starter repo.
Use the juce-setup-ios skill to add an iPad-compatible app target to this starter-based plugin repo.
Use the juce-auto-updates skill to set up Sparkle and run an updater doctor pass.
Use the juce-ci-release skill to check GitHub Actions status and prepare release notes.
Use the juce-project-ops skill to inspect this repo and show any configured cross-platform VMs.
Use the juce-cross-platform-port skill to audit this project for a Windows port.
Use the juce-project-starter skill to explain which .env values I need for code signing.
Use the juce-visage-ui skill to debug keyboard focus in my JUCE + Visage plugin UI.
```

## Related Projects

- `juce-dev` Claude Code plugin: https://www.generouscorp.com/generous-corp-marketplace/plugins/juce-dev/
- `JUCE-Plugin-Starter`: https://github.com/danielraffel/JUCE-Plugin-Starter
- `skills` installer: https://www.npmjs.com/package/skills
