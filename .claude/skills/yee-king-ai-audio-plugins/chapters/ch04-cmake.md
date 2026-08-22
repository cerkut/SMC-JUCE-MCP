# Chapter 4: Installing and using CMake

## Core Idea
Swaps Projucer for CMake as the project generator specifically because CMake integrates cleanly with non-JUCE, CMake-native libraries (libtorch, RTNeural) that Projucer projects can't easily pull in.

## Frameworks Introduced
- **CMake JUCE plugin skeleton**: a minimal but complete `juce_add_plugin(...)` block is the template every later plugin chapter customizes (company name, plugin code, format list, `COPY_PLUGIN_AFTER_BUILD`).

## Key Concepts
- **Generator vs. build**: `cmake -G "<generator>" -B build .` creates IDE project files; `cmake --build build --config Debug|Release` actually compiles.
- **Build kit**: architecture+toolchain pairing (e.g. `amd64` = 64-bit builder+target; `x86_amd64` = 32-bit builder producing a 64-bit binary) — VSCode's "Scan for Kits" surfaces available combinations.
- **`add_subdirectory(../../JUCE ./JUCE)`**: how a CMake project pulls in JUCE — path to JUCE checkout, and where it gets staged inside `build/`.
- **`COPY_PLUGIN_AFTER_BUILD TRUE`**: the CMake equivalent of Projucer's "Enable Plugin Copy Step" (ch.3) — without it, hosts won't find your freshly built plugin.

## Code Examples
```cmake
cmake_minimum_required(VERSION 3.15)
project(minimal_plugin VERSION 0.0.1)
add_subdirectory(../../JUCE ./JUCE)
juce_add_plugin(minimal_plugin
    COMPANY_NAME Yee-King
    IS_SYNTH TRUE
    NEEDS_MIDI_INPUT TRUE
    IS_MIDI_EFFECT FALSE
    NEEDS_MIDI_OUTPUT TRUE
    COPY_PLUGIN_AFTER_BUILD TRUE
    PLUGIN_MANUFACTURER_CODE Yeek
    PLUGIN_CODE Abc1
    FORMATS AU VST3 Standalone
    PRODUCT_NAME "minimal_plugin")

juce_generate_juce_header(minimal_plugin)
target_sources(minimal_plugin PRIVATE
    src/PluginEditor.cpp
    src/PluginProcessor.cpp)
target_compile_definitions(minimal_plugin PUBLIC
    JUCE_DISABLE_CAUTIOUS_PARAMETER_ID_CHECKING=1
    JUCE_USE_OGGVORBIS=1
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0)
target_link_libraries(minimal_plugin
    PRIVATE juce::juce_audio_utils
    PUBLIC juce::juce_recommended_config_flags
           juce::juce_recommended_lto_flags
           juce::juce_recommended_warning_flags)
```
- **What it demonstrates**: the exact minimal-plugin `CMakeLists.txt` every subsequent plugin project in the book is a copy-and-rename of. Every occurrence of `minimal_plugin` (5+ places) must be renamed together per new plugin, plus `COMPANY_NAME`/`PLUGIN_MANUFACTURER_CODE`/`PLUGIN_CODE`/`PRODUCT_NAME` must be made unique per plugin.

## Reference Tables
| Command | Effect |
|---|---|
| `cmake -G "Xcode" -B build .` | generate an Xcode project into `build/` |
| `cmake -G "Visual Studio 17 2022" -B build .` | generate a VS solution |
| `cmake -G "Unix Makefiles" -B build .` | generate Makefiles (Linux default) |
| `cmake --build build --config Debug` | debug build (assertions on, no optimization) |
| `cmake --build build --config Release` | release build (optimized, **overwrites** the debug binary in this simple example) |

## Anti-patterns
- Editing only one occurrence of the plugin's project name in `CMakeLists.txt` — it must be changed consistently across `project()`, `juce_add_plugin()`, `juce_generate_juce_header()`, `target_sources()`, `target_compile_definitions()`, and `target_link_libraries()`.
- Leaving a stray command-line `build/` folder around when switching to VSCode's CMake Tools extension — causes build-folder confusion; delete it first.

## Key Takeaways
1. CMake replaces Projucer from this point forward for every plugin project in the book.
2. The `juce_add_plugin(...)` block's property names (`PLUGIN_CODE`, `PLUGIN_MANUFACTURER_CODE`, `FORMATS`, `COPY_PLUGIN_AFTER_BUILD`) are the fields every later project customizes.
3. Debug and Release builds in this simple setup share one `build/` output — rebuilding Release wipes the Debug binary.

## Connects To
- **Ch 5, 8**: this exact `CMakeLists.txt` template is copied forward for libtorch integration and the first real plugin.
- **Ch 39**: repo-guide section 39.2.2 has the CMake JUCE starter project referenced here.
