# JUCE-MCP: prompt-driven JUCE plugin generator

This repo is a generator shell, not a collection of plugins. Every generated
plugin project (e.g. a folder you or a prior session created) is a local
build artifact — gitignored, never committed. The repo itself only carries
the scaffolding template, the build toolkit, and instructions.

## Submodules

`JUCE-Plugin-Starter/` and `juce-agent-toolkit/` are required and must be
initialized before generating anything:
```bash
git submodule update --init JUCE-Plugin-Starter juce-agent-toolkit
```
`ai-enhanced-audio-book/`, `juce-docs-mcp-server/`, and `JuceMCP-for-agents/`
are optional submodules — initialize individually only if needed (see
README.md).

## Generating a plugin

Two paths, both ending the same way: a new top-level `<plugin-name>/`
directory scaffolded from `JUCE-Plugin-Starter/`, built with CMake/Ninja, and
tested with Catch2.

**From a prompt.** The user describes the DSP/behavior they want. Scaffold via:
```bash
python3 juce-agent-toolkit/shared/scripts/create_project.py "Plugin Name" \
  --starter ./JUCE-Plugin-Starter \
  --destination-parent . \
  --developer-name "<name>"
```
then implement the processor/editor, build (`cmake -B build -G Ninja` inside
the new project dir, then `cmake --build build --target <Name>_Standalone`),
and write Catch2 tests that actually push real audio through `processBlock`
and check for NaN/Inf and no exceptions — not just construction.

**From an arXiv paper + companion GitHub repo.** When the user points at a
paper (e.g. `arxiv:2408.16546`) and its code (e.g.
`https://github.com/abargum/vc-sd-reproduction`):
1. `graphify add arxiv:<id>` — ingests the paper's abstract/metadata into the graph.
2. `graphify clone <github-url>` — clones the companion repo locally, then run
   AST + semantic extraction on it and merge it into the graph as its own
   repo namespace (see `## graphify` below — this graph is a cross-repo merged
   graph; use the manual JSON-union approach documented there, not
   `graphify merge-graphs`, which corrupts existing repo tags on this graph).
3. Read the cloned repo's actual source directly (its README, its inference/
   conversion scripts, any exported model file) to learn the real calling
   convention — don't assume it matches the paper's abstract.
4. Scaffold a new plugin per the prompt-based path above, and build the
   processor around whatever the model actually needs (sample rate, block
   size, stateful vs stateless, named methods vs bare `forward()`, etc.).
   Real-time-safety pattern: decouple audio-thread `processBlock` from model
   inference via a lock-protected queue + a background `juce::Thread` worker;
   never call `torch::jit::script::Module` methods directly on the audio
   thread if inference could be slow.

## graphify

This project has a knowledge graph at `graphify-out/` with god nodes,
community structure, and cross-file relationships. It also functions as a
cross-repo graph — each vendored/submoduled or graphify-added external repo
gets its own `repo::`-prefixed node-ID namespace and a `repo` node attribute
(see existing namespaces: `ai-enhanced-audio-book`, `juce-agent-toolkit`,
`juce-docs-mcp-server`, `JuceMCP-for-agents`, `notes`, `wiki`, `wiki2`).

Rules:
- For codebase questions, first run `graphify query "<question>"` when
  `graphify-out/graph.json` exists. Use `graphify path "<A>" "<B>"` for
  relationships and `graphify explain "<concept>"` for focused concepts.
- If `graphify-out/wiki/index.md` exists, use it for broad navigation instead
  of raw source browsing.
- Read `graphify-out/GRAPH_REPORT.md` only for broad architecture review or
  when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current
  (AST-only, no API cost).
- **When merging a newly `graphify add`-ed or `graphify clone`-ed repo into
  this already-multi-repo graph**: do NOT use `graphify merge-graphs` — it
  derives repo tags from directory basenames and collapses every existing
  distinct `repo` value into generic `repo`/`repo-2` labels, destroying
  provenance across the whole graph. Instead: extract the new content
  (AST + semantic subagents), repo-tag every new node/edge/hyperedge with
  `{repo}::` id prefixes and a `repo` attribute matching the new repo's name,
  then union the resulting nodes/edges/hyperedges directly into
  `graphify-out/graph.json`'s JSON structure (append to `nodes`/`links`/
  `hyperedges`, checking for zero dangling edges afterward). Back up
  `graph.json` before doing this and verify all prior `repo` tags are still
  intact afterward.
