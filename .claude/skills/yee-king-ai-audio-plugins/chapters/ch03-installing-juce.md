# Chapter 3: Installing JUCE

## Core Idea
JUCE gives cross-platform plugin projects with a Standalone build target for fast iteration, tested here by building a Basic Plugin and loading it into JUCE's own `AudioPluginHost`.

## Frameworks Introduced
- **JUCE**: chosen over iPlug2 or direct VST3 SDK use for consistency across platforms, CMake compatibility, and multi-format export (VST3, AU, etc.). Described as "opinionated" but fast to onboard onto.

## Key Concepts
- **Projucer**: JUCE's project-generation hub — creates IDE projects (Xcode/Visual Studio/Linux Makefile) from one `.jucer` config, checks module/exporter setup.
- **Plugin vs. Standalone target**: a plugin target cannot run alone (needs a host); the Standalone target wraps the same code into a runnable app for fast build/test cycles without a DAW.
- **Plugin scan locations**: hosts (including `AudioPluginHost`) discover plugins by scanning fixed OS-specific folders (e.g. `/Library/Audio/Plugins/VST3` on macOS) — the JUCE build's "Enable Plugin Copy Step" must be on for a freshly built plugin to land there.
- **`DBG` macro**: JUCE's console-print facility; needs explicit "redirect to Immediate Window" setup in Visual Studio to be visible at all.

## Reference Tables
| Platform | VST3 plugin scan locations |
|---|---|
| Windows | `C:\Program Files\Common Files\VST3` and `<home>\AppData\Local\Programs\Common\VST3` |
| macOS | `/Library/Audio/Plugins/VST3` and `<home>/Library/Audio/Plugins/VST3` |
| Linux | `/usr/lib/vst3/` and `<home>/.vst3/` |

## Anti-patterns
- Testing every change inside a full DAW during early development — slow/fiddly; use the Standalone target during iteration, and only switch to a real host (Reaper, Cubase, etc.) before sharing.

## Key Takeaways
1. Build the Standalone target for fast iteration; only load into a real host (or `AudioPluginHost`) to confirm true plugin-mode behavior.
2. Plugin discovery depends on the OS-specific install folders — an invisible plugin in a host is often just a missing "copy to plugin folder" build step.
3. `AudioPluginHost` (in `JUCE/extras/AudioPluginHost`) is a free, lightweight graph-based host — good enough for all of this book's testing needs.

## Connects To
- **Ch 4**: swaps Projucer for CMake as the project generator (same JUCE library underneath).
- **Ch 17**: builds a custom `AudioProcessorGraph`-based host, essentially a purpose-built alternative to `AudioPluginHost`.
