# JUCE-MCP

A generator shell for building JUCE audio plugins from natural-language
prompts with Claude Code (or any compatible coding agent) — either from a
plain description, or by pointing at an arXiv paper and its companion GitHub
repo and having the agent turn it into a working plugin.

Clone it, initialize the required submodules, open Claude Code inside it, and
ask for a plugin. Generated plugin projects are local build artifacts —
gitignored, never committed here.

## Quick start

```bash
git clone https://github.com/cerkut/SMC-JUCE-MCP.git
cd SMC-JUCE-MCP
git submodule update --init JUCE-Plugin-Starter juce-agent-toolkit
python3 -m venv .libtorch-venv && .libtorch-venv/bin/pip install torch  # one-time, for neural-FX plugins
```
Then open Claude Code in this directory and describe the plugin you want —
see "Generating a plugin" below.

## What's in this repo

| Path | What it is |
|---|---|
| `JUCE-Plugin-Starter/` (submodule, required) | The CMake/JUCE cross-platform plugin scaffold template (macOS/Windows/Linux, AU/AUv3/VST3/CLAP/Standalone). New plugins are scaffolded from this. |
| `juce-agent-toolkit/` (submodule, required) | Portable build/release workflow scripts — `shared/scripts/create_project.py` (scaffolding), `build_release.py`, and related tooling used to build, test, sign, and package a plugin. |
| `CLAUDE.md` | Instructions for Claude Code: the two generation paths, and how this project's graphify knowledge graph works. |
| `.graphifyignore` | Excludes generated plugins and large vendored/optional submodules from graphify indexing. |

Anything you generate (e.g. a new `my-plugin/` directory) lives alongside
these but is gitignored — it's output, not part of the generator.

## Prerequisites

- **macOS**: Xcode Command Line Tools at minimum (`xcode-select --install`).
  A full Xcode install lets you use the `-G Xcode` generator; without it, use
  `-G Ninja` directly (see Building, below).
- **CMake** and **Ninja** (`brew install cmake ninja`)
- **Python 3** (for the libtorch venv, and for `juce-agent-toolkit`'s scripts)
- **[graphify](https://github.com/safishamsi/graphify)** — used for the
  arXiv-paper/companion-repo generation path (see below); auto-installed by
  its own Claude Code skill on first use if you have one configured, or
  `pip install graphifyy` / `uv tool install graphifyy`.

## One-time setup: libtorch

Neural-FX plugins link against libtorch. There's no official libtorch C++
binary for Apple Silicon, so a generated plugin's `CMakeLists.txt` looks for
the libtorch bundled inside a `pip install torch` wheel instead (it ships
proper CMake config files):

```bash
python3 -m venv .libtorch-venv
.libtorch-venv/bin/pip install torch
```

Run this once at the repo root. Override the location with the
`TORCH_CMAKE_PREFIX_PATH` environment variable if you'd rather keep the venv
elsewhere.

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

## Building a generated plugin

```bash
cd your-plugin-name
cmake -B build -G Ninja
cmake --build build --target <ProjectName>_Standalone
```

(Use `-G Ninja` directly if you don't have a full Xcode install — the
project's own `generate_and_open_xcode.sh` assumes Xcode is available.)

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
