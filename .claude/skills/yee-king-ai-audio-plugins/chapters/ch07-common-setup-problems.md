# Chapter 7: Common development environment setup problems

## Core Idea
A troubleshooting reference for the Part 1 setup chain — most useful as a lookup table when a build breaks, not as sequential reading.

## Reference Tables
| Problem | Fix |
|---|---|
| Projucer-generated project doesn't recognize JUCE | Regenerate a fresh project, compare module/exporter settings against the broken one |
| VS complains about v143 toolkit missing | Re-run VS Installer, add the v143+ C++ package, or pick a different platform toolset in Projucer's exporter |
| Fresh Projucer project fails to build at all | Missing IDE components — VS C++ workload / Xcode command line tools / Linux `build-essential` |
| libtorch + JUCE: `nullopt` is ambiguous | `JuceHeader.h` does `using namespace juce`, colliding with libtorch's own global-namespace symbols — include individual JUCE headers instead of the umbrella `JuceHeader.h` |
| Compiler rejects basic syntax (e.g. constructor initializer lists) | Project defaulting to pre-C++11 — add `set_property(TARGET project-name PROPERTY CXX_STANDARD 14)` to CMakeLists.txt |

## Anti-patterns
- Including the umbrella `JuceHeader.h` in a file that also uses libtorch — the `using namespace juce` it triggers collides with libtorch's own symbols (`nullopt` ambiguity is the classic symptom).

## Key Takeaways
1. The `nullopt`-ambiguous error is specifically a JUCE+libtorch namespace collision — fix by including individual JUCE headers, not `JuceHeader.h`.
2. If the compiler rejects modern C++ syntax, explicitly pin `CXX_STANDARD` in CMakeLists.txt rather than assuming a sane default.

## Connects To
- **Ch 5**: the JUCE+libtorch combination that produces the `nullopt` error.
- **Ch 4**: the CMakeLists.txt structure `CXX_STANDARD` gets added to.
