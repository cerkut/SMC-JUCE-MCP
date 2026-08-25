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

Three paths, all ending the same way: a new `<plugin-name>/` directory
scaffolded from `JUCE-Plugin-Starter/` as a **sibling of this repo** (one
level up — see `--destination-parent ..` below), built with CMake/Ninja, and
tested with Catch2. Scaffolding outside this working tree is deliberate: it
means a generated project never needs its own `.gitignore` entry here. Works
the same way on macOS, Windows, and Linux — see "Cross-platform CMake
snippets" below for the canonical patterns any neural-FX plugin needs to
actually build on all three.

Use `uv` for any Python tooling a generated plugin or this workflow needs
(`uv venv`, `uv pip install`, `uv tool install`) — not plain `pip`/
`python -m venv`. See README.md's "One-time setup: libtorch" for the exact
commands.

**From a prompt.** The user describes the DSP/behavior they want. Scaffold via:
```bash
python3 juce-agent-toolkit/shared/scripts/create_project.py "Plugin Name" \
  --starter ./JUCE-Plugin-Starter \
  --destination-parent .. \
  --developer-name "<name>"
```
then implement the processor/editor, build (`cmake -B build -G Ninja` inside
the new project dir, then `cmake --build build --target <Name>_Standalone`),
and write Catch2 tests that actually push real audio through `processBlock`
and check for NaN/Inf and no exceptions — not just construction.

**From an arXiv paper + companion GitHub repo.** When the user points at a
paper (e.g. `arxiv:2309.02265`, PESTO) and its code (e.g.
`https://github.com/SonyCSLParis/pesto`):
1. `graphify add https://arxiv.org/abs/<id>` — ingests the paper's
   abstract/metadata into the graph. **Use the `https://arxiv.org/abs/<id>`
   form, not the bare `arxiv:<id>` scheme** — confirmed the CLI's URL
   validator rejects `arxiv:` outright ("Blocked URL scheme 'arxiv' — only
   http and https are allowed"), even though the scheme is used informally
   elsewhere in this doc and in conversation to refer to a paper.
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

Confirmed twice with real pitch-tracking models (PESTO → Pesto Pitch
Tracker, CREPE via `github.com/maxrmorrison/torchcrepe` → Crepe Pitch
Tracker): bake normalization, decoding, and unit conversion into the traced
TorchScript export itself (not left for C++ to reimplement) so the plugin's
`forward()` call is a single opaque step — raw audio samples in, `(hz,
confidence)` out. The two models needed different feed shapes despite both
being pitch trackers: PESTO takes small non-overlapping chunks (441 samples
@44.1kHz) fed directly; CREPE takes a much longer window (1024 samples
@16kHz) relative to a sensible hop (160 samples), so consecutive inference
windows *overlap* — the worker thread must maintain a rolling window buffer
sliding by one hop per iteration, not just clear-and-refill a queue. Always
confirm which shape a new model needs by reading its actual preprocessing
code rather than assuming one pattern fits all pitch trackers.

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
   - **Same rule applies to `AU_EXPORT_PREFIX`** on macOS, independent of
     Unity: if it's set to `"${PROJECT_NAME}AU"` and `PROJECT_NAME` is
     hyphenated, the AU target fails to compile (`AU_EXPORT_PREFIX` is used
     verbatim as a C symbol/macro name, and hyphens aren't legal there
     either). Confirmed on Pesto Pitch Tracker. Set `AU_EXPORT_PREFIX`
     explicitly to a hyphen-free string (e.g. the same value as
     `PRODUCT_NAME` + `"AU"`), not derived from `PROJECT_NAME`.
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

## Any plugin that reads live microphone/audio input

If the plugin's `processBlock` is meant to analyze or process **live input**
(not just host playback — a pitch tracker, a voice-conversion plugin, a mic
effect), add `MICROPHONE_PERMISSION_ENABLED TRUE` and a
`MICROPHONE_PERMISSION_TEXT "..."` to the `juce_add_plugin(...)` call.
**Confirmed twice** (S-RAVE, Pesto Pitch Tracker) that skipping this is a
silent failure, not an error: without `NSMicrophoneUsageDescription` in the
built `Info.plist`, macOS never prompts for mic access, so the Standalone app
launches fine, the UI looks fine, and `processBlock` just receives silence
forever — no crash, no error message, nothing to grep in logs. Verify by
checking the built `Info.plist` (`plutil -p .../Info.plist | grep -i
microphone`) before telling the user to test with real input. If a plugin
was already built without this and the user reports "nothing happens with
mic input", add the flag, rebuild, and run
`tccutil reset Microphone <bundle-id>` (bundle ID is in the same `Info.plist`)
so the next launch re-prompts instead of silently reusing a stale denial.

## Verify a pretrained checkpoint actually downloads before committing to it

READMEs go stale. **Confirmed on Torch DDSP**: both `acids-ircam/ddsp_pytorch`'s
documented pretrained checkpoints (saxophone, violin — IRCAM Nubo share
links) and the repo literally named `torch-ddsp`
(`github.com/chloelavrat/torch-ddsp`, no `train.py`/`export.py`/weights at
all, explicitly "in re-development") turned out to have **no usable
checkpoint whatsoever** — the Nubo links 404, no mirror, no GitHub release.
Before scaffolding a plugin around any pretrained-model source: actually
`curl -L -o /tmp/test.ext <url>` (or equivalent) and confirm it's the real
file (right size, right magic bytes — a 404 page saved to a `.ts` file is a
few KB of HTML, not tens/hundreds of MB of binary), not just that the
README *mentions* a download link. If nothing pans out, tell the user and
let them choose: train a quick demo checkpoint, use a different source
repo/checkpoint, or proceed with untrained weights — don't silently
fabricate or substitute. For Torch DDSP the resolution was substituting a
different but task-equivalent architecture with real, live checkpoints:
[RAVE](https://github.com/acids-ircam/RAVE) (same IRCAM ACIDS team, same
real-time timbre-transfer use case, a VAE rather than a DDSP harmonic+noise
synthesizer) via a checkpoint from
`huggingface.co/Intelligent-Instruments-Lab/rave-models`. RAVE's exported
TorchScript module is a genuinely simple, fully self-contained streaming
autoencoder — `forward(x) = decode(encode(x))`, shape-preserving
(`(1,1,N)` in and out, `N` = the checkpoint's trained buffer size, e.g.
2048 in a `..._b2048_...` filename), stateful across calls via its own
registered buffers (no explicit reset method needed, unlike S-RAVE) — the
simplest of the neural-FX integration patterns in this repo so far.

**No instrument-specific checkpoint always exists.** Confirmed on Voice To
Cello (a "convert my voice to a cello sound" request): there is no public
cello-only RAVE checkpoint anywhere — checked IRCAM's own forum API
(`play.forum.ircam.fr/rave-vst-api/get_available_models`, which lists every
model IRCAM currently hosts), Hugging Face, and community repos. When the
requested instrument/timbre isn't covered, look for the closest real,
verified checkpoint rather than stalling — `musicnet` (trained on the
MusicNet dataset of solo/chamber classical recordings: cello, violin,
piano, winds) was the closest available, and its calling convention is
identical to the guitar checkpoint above (same `encode_params`/
`decode_params` shape, `forward(x) = decode(encode(x), true)`). Tell the
user explicitly that the result leans "melodic chamber ensemble" rather
than isolated cello, since no model constrains it to one instrument.
Also worth knowing generally: these RAVE checkpoints' raw output level can
run ~20-30dB below the input's for typical program material (verified by
feeding a 0.3-amplitude test tone and measuring the output range before
wiring up gain staging) — add a makeup-gain parameter rather than assuming
unity output level.

## Pretrained models with a narrower usable range than their raw input allows

When wrapping a pretrained analysis model (pitch tracker, classifier, etc.)
that was trained on a specific content domain, its *architectural* input
range (e.g. a CQT's fmin/fmax) can be much wider than the range it actually
produces confident/correct output for — the two are easy to conflate.
**Confirmed on Pesto Pitch Tracker**: the `mir-1k_g7` checkpoint (PESTO,
trained on the MIR-1K *singing voice* dataset) has a CQT input range up to
~4.2kHz, but empirically its confidence output collapses to ~0 above
~1.2kHz — it was never trained on content that high, even though nothing
stops you from feeding it there. The user-visible symptom was "pitch
tracking doesn't work for whistling" (typical whistle pitch is 1-3kHz),
which looked like a bug but was actually the model working exactly as
trained, on the wrong input range.

Diagnose this by testing the exported model directly against synthetic
sine tones spanning the range you actually need (not just the range you
assumed), and inspect both the estimate and the confidence/probability
output — a wrong-but-confident estimate and a right-but-unconfident one
are different failure modes needing different fixes:
```python
model = torch.jit.load("model.pt")
for f in [220, 440, 800, 1000, 1500, 2000, 2500, 3000]:
    # feed chunk-sized synthetic sine at f, print (recovered_hz, confidence)
```
If confidence craters well before the input range's theoretical limit, one
fix (verified working here) is an **octave-shift trick**: resample the
audio fed to the model so a true frequency `f` appears to it as `f / N`
(inside its confident range), then multiply the model's output by `N` to
recover the true frequency. Concretely: resample to `N ×` the model's
native rate before chunking (so each fixed-size chunk spans `1/N` the real
time, containing `1/N` the cycles a true `f` would normally produce), and
multiply the recovered Hz by `N` on the way out. This is a real-content
transform (like the host-rate→model-rate resampling every neural-FX plugin
here already does), not a hack specific to any one model — same technique
applies to any narrow-range pretrained analyzer.

## Cross-platform CMake snippets

Canonical patterns for anything a generated plugin's `CMakeLists.txt` needs
to work identically on macOS, Windows, and Linux. Use these verbatim (adapted
to the plugin's own `PROJECT_NAME`/`TORCH_LIBRARIES` etc.) rather than
re-deriving them — the versions below fix real cross-platform gaps found in
earlier generated plugins.

**libtorch venv detection** (checks both Unix and Windows venv layouts, and
both the old in-repo location and the current sibling-of-repo location — see
"Generating a plugin" above: generated projects scaffold as siblings of this
repo via `--destination-parent ..`, so `.libtorch-venv` normally lives inside
*some* sibling directory, e.g. `../JUCE-MCP/.libtorch-venv`, not directly in
`..` — the wildcard middle path segment below matches that regardless of what
the generator repo's clone directory happens to be named):
```cmake
if(DEFINED ENV{TORCH_CMAKE_PREFIX_PATH})
    list(APPEND CMAKE_PREFIX_PATH "$ENV{TORCH_CMAKE_PREFIX_PATH}")
else()
    file(GLOB _torch_venv_cmake
        "${CMAKE_SOURCE_DIR}/../.libtorch-venv/lib/python3.*/site-packages/torch/share/cmake"    # Unix, old in-repo layout
        "${CMAKE_SOURCE_DIR}/../.libtorch-venv/Lib/site-packages/torch/share/cmake"               # Windows, old in-repo layout
        "${CMAKE_SOURCE_DIR}/../*/.libtorch-venv/lib/python3.*/site-packages/torch/share/cmake"  # Unix, sibling generator repo
        "${CMAKE_SOURCE_DIR}/../*/.libtorch-venv/Lib/site-packages/torch/share/cmake")            # Windows, sibling generator repo
    if(_torch_venv_cmake)
        list(APPEND CMAKE_PREFIX_PATH "${_torch_venv_cmake}")
    endif()
endif()
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")
```
(An earlier version of this snippet, still present in some already-generated
local plugin dirs, only had the Unix glob — `find_package(Torch)` silently
found nothing on Windows unless `TORCH_CMAKE_PREFIX_PATH` was set manually.
A later version only checked the old in-repo `../.libtorch-venv` path, which
silently stopped matching anything once generated plugins moved to being
scaffolded as repo siblings rather than repo children — confirmed on Crepe
Pitch Tracker.)

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
