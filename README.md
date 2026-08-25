# JUCE-MCP

A generator shell for building JUCE audio plugins from natural-language
prompts with Claude Code (or any compatible coding agent) — from a plain
description, by pointing at an arXiv paper and its companion GitHub repo, or
targeting Unity's native audio plugin format in addition to VST3/AU/Standalone.

Clone it, initialize the required submodules, open Claude Code inside it, and
ask for a plugin. Generated plugin projects are local build artifacts —
gitignored, never committed here. Works on macOS, Windows, and Linux.

## Quick start

```bash
git clone https://github.com/cerkut/SMC-JUCE-MCP.git
cd SMC-JUCE-MCP
git submodule update --init JUCE-Plugin-Starter juce-agent-toolkit
uv venv .libtorch-venv && uv pip install --python .libtorch-venv/bin/python torch  # one-time, for neural-FX plugins (Windows: .libtorch-venv\Scripts\python.exe)
```
Then open Claude Code in this directory and describe the plugin you want —
see "Generating a plugin" below.

## What's in this repo

| Path | What it is |
|---|---|
| `JUCE-Plugin-Starter/` (submodule, required) | The CMake/JUCE cross-platform plugin scaffold template (macOS/Windows/Linux, AU/AUv3/VST3/CLAP/Standalone/Unity). New plugins are scaffolded from this. |
| `juce-agent-toolkit/` (submodule, required) | Portable build/release workflow scripts — `shared/scripts/create_project.py` (scaffolding), `build_release.py`, and related tooling used to build, test, sign, and package a plugin. |
| `CLAUDE.md` | Instructions for Claude Code: the generation paths, the canonical cross-platform CMake snippets, and how this project's graphify knowledge graph works. |
| `.graphifyignore` | Excludes generated plugins and large vendored/optional submodules from graphify indexing. |

Anything you generate (e.g. a new `my-plugin/` directory) lives alongside
these but is gitignored — it's output, not part of the generator.

## Prerequisites

Install [uv](https://docs.astral.sh/uv/) first — used for all Python tooling
in this repo (the libtorch venv, graphify) instead of plain `pip`:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then, per platform:

- **macOS**: Xcode Command Line Tools at minimum (`xcode-select --install`).
  A full Xcode install lets you use the `-G Xcode` generator; without it, use
  `-G Ninja` directly (see Building, below). CMake/Ninja: `brew install cmake ninja`.
- **Windows**: Visual Studio 2022 (Community or Build Tools) with the C++
  workload, plus CMake/Ninja via `winget install cmake ninja` — or run
  `JUCE-Plugin-Starter/scripts/dependencies.sh` from Git Bash/WSL once that
  submodule is initialized, which handles this automatically.
- **Linux**: `sudo apt install cmake ninja-build clang` plus JUCE's own
  library dependencies — or run `JUCE-Plugin-Starter/scripts/dependencies.sh`,
  which installs everything needed in one pass.
- **[graphify](https://github.com/safishamsi/graphify)** — used for the
  arXiv-paper/companion-repo generation path (see below); auto-installed by
  its own Claude Code skill on first use if you have one configured, or
  `uv tool install graphifyy` (plain `pip install graphifyy` also works if
  you'd rather not use uv here).

## One-time setup: libtorch

Neural-FX plugins link against libtorch. There's no official libtorch C++
binary for Apple Silicon, so a generated plugin's `CMakeLists.txt` looks for
the libtorch bundled inside a `pip install torch` wheel instead (it ships
proper CMake config files) — this also happens to be the most portable
approach on Windows/Linux, so it's used everywhere, not just macOS:

```bash
uv venv .libtorch-venv
uv pip install --python .libtorch-venv/bin/python torch      # macOS / Linux
uv pip install --python .libtorch-venv\Scripts\python.exe torch  # Windows
```

Run this once at the repo root. Override the location with the
`TORCH_CMAKE_PREFIX_PATH` environment variable if you'd rather keep the venv
elsewhere. See `CLAUDE.md` for the canonical CMake snippet that locates this
venv's libtorch — it checks both Unix (`lib/pythonX.Y/site-packages/...`) and
Windows (`Lib/site-packages/...`) venv layouts.

## Generating a plugin

**From a prompt.** Describe the DSP/behavior you want. Claude scaffolds a new
project from `JUCE-Plugin-Starter` via `juce-agent-toolkit`'s creation
script, implements it, and builds/tests it:

```bash
python3 juce-agent-toolkit/shared/scripts/create_project.py "Your Plugin Name" \
  --starter ./JUCE-Plugin-Starter \
  --destination-parent . \
  --developer-name "Your Name"
```
(Windows note: this needs `python3` specifically on `PATH`, not just
`python` — see "Windows/Linux notes" below if it's not found.)

**From an arXiv paper + its code.** Point at a paper and its companion GitHub
repo — e.g. `arxiv:2408.16546` and
[abargum/vc-sd-reproduction](https://github.com/abargum/vc-sd-reproduction) —
and Claude will: ingest the paper and clone+ingest the repo into this
project's graphify knowledge graph, read the actual source to learn the
model's real calling convention (sample rate, statefulness, named methods),
then scaffold and implement a plugin around it. See `CLAUDE.md` for the exact
graphify commands and the real-time-safety pattern used (a background worker
thread decoupled from the audio thread via a lock-protected queue — needed
whenever model inference is too slow to run inline in `processBlock`).

**Targeting Unity.** In addition to VST3/AU/Standalone, a generated plugin
can build as a Unity native audio plugin — no separate Unity SDK or Editor
install needed to build it (JUCE reimplements the necessary parts of Unity's
Native Audio Plugin API itself). Add `Unity` to the project's
`PLUGIN_FORMATS`/`FORMATS` list; see `CLAUDE.md` for the exact steps and a
sharp gotcha confirmed by an actual build: **the generated Unity C# glue
script uses `PRODUCT_NAME` verbatim as a C# class name, so a hyphenated
product name (e.g. the default `your-plugin-name` from the scaffolding
script) produces invalid C# and won't compile inside Unity** — use a
hyphen-free `PRODUCT_NAME` (e.g. `YourPluginName`) whenever Unity is in the
format list.

## Building a generated plugin

```bash
cd your-plugin-name
cmake -B build -G Ninja
cmake --build build --target <ProjectName>_Standalone
```

This is the cross-platform path (works identically on macOS/Windows/Linux
shells). Platform-specific alternatives, if you prefer them:
- **macOS**: `./scripts/generate_and_open_xcode.sh` (requires a full Xcode install, not just Command Line Tools)
- **Windows**: `.\scripts\build.ps1 standalone`
- **Linux**: `./scripts/build.sh standalone` (auto-detects Linux, uses Ninja)

## Windows/Linux notes

- `create_project.py` (in `juce-agent-toolkit`) shells out to `python3`
  specifically. On Windows, if only `python`/`py` are on `PATH`, either
  enable the Python installer's "Add python.exe to PATH" + a `python3.bat`
  shim, or run it from Git Bash/WSL, where `python3` is typically already
  aliased.
- Some of `JUCE-Plugin-Starter`'s helper scripts (e.g. `setup_visage.sh`) are
  POSIX shell scripts with no native Windows equivalent — run those from Git
  Bash or WSL if you need them; they're opt-in, not part of the core
  generation flow.
- The libtorch venv-detection CMake snippet (see `CLAUDE.md`) already handles
  both Unix and Windows venv layouts, so `find_package(Torch)` works the same
  way on all three platforms once the venv exists.

## Optional submodules

Not required for generation — initialize individually only if you want them locally:

```bash
git submodule update --init ai-enhanced-audio-book    # book source (already queryable via graphify without this)
git submodule update --init juce-docs-mcp-server       # JUCE class-docs MCP server (TypeScript/Node)
git submodule update --init JuceMCP-for-agents         # JUCE class-docs MCP server (Python)
```

- **[ai-enhanced-audio-book](https://github.com/yeeking/ai-enhanced-audio-book)** — source/example code from *Build AI-Enhanced Audio Plugins with C++* (Matthew Yee-King). Queryable via `graphify query` under the `ai-enhanced-audio-book` repo namespace even without initializing this submodule locally.
- **[juce-docs-mcp-server](https://github.com/danielraffel/juce-docs-mcp-server)** (TypeScript/Node) and **[JuceMCP-for-agents](https://github.com/stefbil/JuceMCP-for-agents)** (Python) — give an agent lookup access to JUCE class documentation.

Not included at all: **agent-skills** ([shortwavlabs/agent-skills](https://github.com/shortwavlabs/agent-skills)) — a Pure Data/plugdata patch-generation skill, a different (non-JUCE) audio environment.

## License

Not yet chosen for this repo's own content. Each submodule is governed by its
own upstream license.
