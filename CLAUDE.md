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

Three paths, all ending the same way: a new top-level `<plugin-name>/`
directory scaffolded from `JUCE-Plugin-Starter/`, built with CMake/Ninja, and
tested with Catch2. Works the same way on macOS, Windows, and Linux — see
"Cross-platform CMake snippets" below for the canonical patterns any
neural-FX plugin needs to actually build on all three.

Use `uv` for any Python tooling a generated plugin or this workflow needs
(`uv venv`, `uv pip install`, `uv tool install`) — not plain `pip`/
`python -m venv`. See README.md's "One-time setup: libtorch" for the exact
commands.

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

**Targeting Unity.** `Unity` is a first-class, built-in `FORMATS` value for
JUCE's `juce_add_plugin()` (confirmed against the JUCE 8.0.12 this repo
pins) — no external Unity SDK or Editor download is needed to *build* it;
JUCE reimplements the necessary parts of Unity's Native Audio Plugin API
itself (`juce_audio_plugin_client_Unity.cpp` +
`Unity/juce_UnityPluginInterface.h`, both self-contained).
1. In the generated project's `CMakeLists.txt`, add `Unity` to the
   `PLUGIN_FORMATS`/`FORMATS` list (same list `AU`/`VST3`/`Standalone` are
   already in).
2. **Set `PRODUCT_NAME` to something with no hyphens** (e.g. `MyPlugin`, not
   `my-plugin`) whenever `Unity` is in the format list. Confirmed by an
   actual build: JUCE's generated Unity C# glue script uses `PRODUCT_NAME`
   verbatim as a C# class name (`public class {PRODUCT_NAME}GUI : ...`), and
   hyphens are illegal in C# identifiers — a hyphenated product name (the
   scaffolding script's default) produces a `.cs` file that fails to compile
   inside Unity. `PROJECT_NAME` (the folder/CMake target name) can keep its
   hyphen; only `PRODUCT_NAME` needs to change if they're set to different
   values.
3. Keep the plugin a pure audio effect — `IS_MIDI_EFFECT FALSE`,
   `NEEDS_MIDI_INPUT/OUTPUT FALSE` (already how every plugin generated here
   is configured; Unity's native audio callback has no MIDI path).
4. Build the `<ProjectName>_Unity` target. Output: `.bundle` (macOS,
   installs by default to `~/Library/Audio/Plug-Ins/Unity/`), `.dll`
   (Windows, `%APPDATA%/Unity`), `.so` (Linux, `~/.unity`) — plus an
   auto-generated `<ProjectName>_UnityScript.cs` glue file placed alongside
   it (macOS: inside the bundle's `Contents/Resources/`). These default
   install locations are **not** a Unity project's `Assets/Plugins/` — pass
   `UNITY_COPY_DIR "<path-to-unity-project>/Assets/Plugins"` to
   `juce_add_plugin(...)` if you know the target project's path, so the
   build lands the plugin + script directly where Unity will discover them.
5. Confirmed by the same test build: the default Apple bundle install path
   (no `XCODE_ATTRIBUTE_INSTALL_PATH` override needed for `_Unity`, unlike
   the `_VST3`/`_Standalone` overrides already present in generated
   `CMakeLists.txt` files) worked correctly out of the box — no fix needed
   there.

## Cross-platform CMake snippets

Canonical patterns for anything a generated plugin's `CMakeLists.txt` needs
to work identically on macOS, Windows, and Linux. Use these verbatim (adapted
to the plugin's own `PROJECT_NAME`/`TORCH_LIBRARIES` etc.) rather than
re-deriving them — the versions below fix real cross-platform gaps found in
earlier generated plugins.

**libtorch venv detection** (checks both Unix and Windows venv layouts):
```cmake
if(DEFINED ENV{TORCH_CMAKE_PREFIX_PATH})
    list(APPEND CMAKE_PREFIX_PATH "$ENV{TORCH_CMAKE_PREFIX_PATH}")
else()
    file(GLOB _torch_venv_cmake
        "${CMAKE_SOURCE_DIR}/../.libtorch-venv/lib/python3.*/site-packages/torch/share/cmake"  # Unix
        "${CMAKE_SOURCE_DIR}/../.libtorch-venv/Lib/site-packages/torch/share/cmake")            # Windows
    if(_torch_venv_cmake)
        list(APPEND CMAKE_PREFIX_PATH "${_torch_venv_cmake}")
    endif()
endif()
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")
```
(An earlier version of this snippet, still present in some already-generated
local plugin dirs, only had the Unix glob — `find_package(Torch)` silently
found nothing on Windows unless `TORCH_CMAKE_PREFIX_PATH` was set manually.)

**Windows torch DLL copy** (loop over every built format, not just `_Standalone`):
```cmake
if(MSVC)
    file(GLOB TORCH_DLLS "${TORCH_INSTALL_PREFIX}/lib/*.dll")
    foreach(_fmt ${PLUGIN_FORMATS})
        if(TARGET ${PROJECT_NAME}_${_fmt})
            add_custom_command(TARGET ${PROJECT_NAME}_${_fmt} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    ${TORCH_DLLS}
                    $<TARGET_FILE_DIR:${PROJECT_NAME}_${_fmt}>)
        endif()
    endforeach()
endif()
```
(An earlier version only copied DLLs next to `_Standalone`, leaving `_VST3`/
other Windows formats unable to find libtorch at runtime.)

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
