# JUCE-MCP

A self-contained workspace for generating, building, and deploying JUCE audio
plugins from natural-language prompts with Claude Code (or any compatible
coding agent). Clone it and everything needed to go from a prompt to a built
plugin is already here — no external skill or template repos required.

## What's in this repo

| Path | What it is |
|---|---|
| `.claude/skills/yee-king-ai-audio-plugins/` | Knowledge base distilled from *Build AI-Enhanced Audio Plugins with C++* (Matthew Yee-King) — JUCE plugin dev, libtorch/RTNeural neural FX, interactive ML control, Markov sequencing, classical DSP. Load a chapter instead of re-deriving the theory. |
| `JUCE-Plugin-Starter/` | The CMake/JUCE cross-platform plugin scaffold template (macOS/Windows/Linux, AU/AUv3/VST3/CLAP/Standalone). New plugins are scaffolded from this. |
| `juce-agent-toolkit/` | Portable build/release workflow skills and scripts — `shared/scripts/create_project.py` (scaffolding), `build_release.py`, and related tooling used to build, test, sign, and package a plugin. |
| `demo-plugin/` | Worked example: an LSTM neural audio effect (TorchScript/libtorch), built on JUCE-Plugin-Starter, with runtime model-swapping and Catch2 tests. |
| `steinmetz-reverb/` | Worked example: a TCN-based steerable neural reverb (Steinmetz & Reiss), with a real-time-safe block-decoupled inference architecture and tests. |
| `CLAUDE.md` | Project instructions for Claude Code — points at the skill above, plus optional add-ons. |

Both example plugins double as regression checks: if they still configure and
build cleanly, the toolchain (JUCE, libtorch, CMake/Ninja) is set up correctly.

## Prerequisites

- **macOS**: Xcode Command Line Tools at minimum (`xcode-select --install`).
  A full Xcode install lets you use the `-G Xcode` generator; without it, use
  `-G Ninja` directly (see Building, below).
- **CMake** and **Ninja** (`brew install cmake ninja`)
- **Python 3** (for the libtorch venv, and for `juce-agent-toolkit`'s scripts)

## One-time setup: libtorch

The neural-FX plugins (`demo-plugin`, `steinmetz-reverb`) link against
libtorch. There's no official libtorch C++ binary for Apple Silicon, so both
projects' `CMakeLists.txt` look for the libtorch bundled inside a `pip install
torch` wheel instead (it ships proper CMake config files):

```bash
python3 -m venv .libtorch-venv
.libtorch-venv/bin/pip install torch
```

Run this once at the repo root. Override the location with the
`TORCH_CMAKE_PREFIX_PATH` environment variable if you'd rather keep the venv
elsewhere.

## Generating a new plugin

Scaffold a new plugin from `JUCE-Plugin-Starter` using the toolkit's creation
script — this is the same command used to produce both example plugins:

```bash
python3 juce-agent-toolkit/shared/scripts/create_project.py "Your Plugin Name" \
  --starter ./JUCE-Plugin-Starter \
  --destination-parent . \
  --developer-name "Your Name"
```

From there, describe the DSP/behavior you want in a prompt to Claude Code —
it can draw on the `yee-king-ai-audio-plugins` skill for JUCE/neural-audio
patterns and `juce-agent-toolkit`'s build/release skills to build, test, and
package the result.

## Building an example plugin

```bash
cd demo-plugin   # or steinmetz-reverb
cmake -B build -G Ninja
cmake --build build --target <ProjectName>_Standalone
```

(Use `-G Ninja` directly if you don't have a full Xcode install — the
project's own `generate_and_open_xcode.sh` assumes Xcode is available.)

## Optional add-ons (not included here)

Not required for generation or building — clone separately if you want them:

- **JUCE class-docs MCP servers**: [danielraffel/juce-docs-mcp-server](https://github.com/danielraffel/juce-docs-mcp-server) (TypeScript/Node) and [stefbil/JuceMCP-for-agents](https://github.com/stefbil/JuceMCP-for-agents) (Python) — give an agent lookup access to JUCE class documentation.
- **ai-enhanced-audio-book**: [yeeking/ai-enhanced-audio-book](https://github.com/yeeking/ai-enhanced-audio-book) — the book's raw source and example code; already distilled into the skill above.
- **agent-skills** ([shortwavlabs/agent-skills](https://github.com/shortwavlabs/agent-skills)): a Pure Data/plugdata patch-generation skill — a different (non-JUCE) audio environment.

## License

Not yet chosen for this repo's own content. `JUCE-Plugin-Starter/LICENSE` and
`juce-agent-toolkit/LICENSE` are preserved as-is and govern those
subdirectories under their own terms.
