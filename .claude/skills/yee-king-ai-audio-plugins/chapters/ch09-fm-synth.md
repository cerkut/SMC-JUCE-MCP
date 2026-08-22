# Chapter 9: FM synthesizer plugin

## Core Idea
Adds a second oscillator (frequency modulation) to the Ch.8 sine plugin, then exposes its two new controls both as GUI sliders *and* as host-visible `AudioParameterFloat` plugin parameters — the FM plugin that becomes the meta-controller's target synth later.

## Frameworks Introduced
- **Two-oscillator FM synthesis**: `mod = sin(mod_phase) * mod_depth`; carrier `dphase` is recomputed each sample as `getDPhase(frequency + mod, sampleRate)`. Modulator frequency itself = `frequency * mod_index`.

## Key Concepts
- **`juce::AudioParameterFloat`**: registers a parameter with the host (`addParameter(...)`) so it appears for automation/presets *and* in a host-auto-generated generic UI — distinct from, and eventually replacing, a plain member variable driven only by a custom GUI slider.
- **Dual UI paths**: a plugin can expose both a custom `PluginEditor` UI and the host's auto-generated parameter UI simultaneously — both must stay in sync by reading/writing the same `AudioParameterFloat*`.

## Code Examples
```cpp
// FM synthesis inside processBlock (replaces plain sine generation)
channelData[sInd] = (float)(std::sin(phase) * amp);
mod = std::sin(mod_phase);
mod *= mod_depth;
dphase = getDPhase(frequency + mod, getSampleRate());
phase += dphase;
mod_phase += mod_dphase;
```
```cpp
// exposing mod index/depth as host-visible parameters
modIndexParam = new juce::AudioParameterFloat("ModInd", "Mod index", 0.0f, 10.0f, 0.5f);
addParameter(modIndexParam);
modDepthParam = new juce::AudioParameterFloat("ModDep", "Mod depth", 0.0f, 1000.0f, 100.0f);
addParameter(modDepthParam);

// reading params back into the synthesis state, inside processBlock
mod_dphase = getDPhase(frequency * static_cast<double>(*modIndexParam), getSampleRate());
mod_depth = static_cast<double>(*modDepthParam);
```
- **What it demonstrates**: once parameters exist, setters (`setModIndex`/`setModDepth`) should mutate the `AudioParameterFloat*` (`*modIndexParam = newIndex`) instead of a plain double — the GUI slider and the host parameter must read/write the *same* underlying value.

## Anti-patterns
- Leaving GUI sliders writing to plain member variables *after* introducing `AudioParameterFloat`s — the two state stores silently diverge; the setters must be updated to write through the parameter object.
- Using `std::sin` for real-time oscillators in a production plugin — acceptable here for two oscillators, but JUCE's own oscillator classes are more efficient at scale.

## Key Takeaways
1. FM synthesis is two oscillators: `carrier_dphase = getDPhase(frequency + modulator_output, sampleRate)`, recomputed every sample.
2. `AudioParameterFloat` + `addParameter()` is how a plugin exposes automatable, preset-compatible parameters to a host — plain member variables are invisible to the host.
3. This FM plugin is the target instrument the meta-controller (Ch.12+) will learn to control — its parameter count and ranges matter later.

## Connects To
- **Ch 13**: this exact FM plugin becomes the Superknob's controlled synth.
- **Ch 19**: generalizes "expose plugin parameters to a host" into "query *any* plugin's parameters" for the full meta-controller.
