# Chapter 30: Waveshapers

## Core Idea
The third DSP Trinity member: nonlinear transfer functions (ReLU, sigmoid, clip) applied sample-by-sample. Built three ways — raw WAV processing, a "DIY" plugin, and a `ProcessorChain`-based plugin with a parameterized lambda — then chained with IIR + Convolution into a simple multi-stage guitar amp emulator.

## Frameworks Introduced
- **Fractal Audio's guitar amp signal-chain model**: pre-amp (fixed EQ filtering + non-linear distortion) → tone stage (adjustable EQ) → power amp (distortion again) → speaker cabinet (acoustic response). Maps directly onto the DSP Trinity: **pre-amp = IIR + waveshaper; tone = IIR; power amp = waveshaper; cabinet = FIR/convolution** (captured impulse response). This is the DSP-only precursor the neural amp model (Ch.31+) eventually replaces/augments.

## Key Concepts
- **Waveshaping = nonlinear transfer function per-sample**: `relu(x) = max(0, x)`; `sigmoid(x) = 1/(1+e^-x)`; `clip(x, t) = ±1 if |x| > t else x`. Each produces a characteristically different distortion timbre.
- **JUCE `dsp::WaveShaper` uses a lambda** (`functionToUse`) for its transfer function — a C++ lambda `[](float x){...}` is like a JS anonymous function; the `[]` capture-list controls what scope (e.g. `this`) the lambda can see.
- **Parameterizing a lambda**: the default `WaveShaper<float>` template only allows a capture-less function; switching to `WaveShaper<float, std::function<float(float)>>` allows `[this](float x){...}`, giving the lambda access to a live `AudioParameterFloat` (e.g. `clipThreshold`) — this is what makes the clip point dynamically controllable instead of hardcoded.
- **`GenericAudioProcessorEditor`**: JUCE auto-generates a UI slider for any registered `AudioParameterFloat`, useful for quick prototyping without hand-building a `PluginEditor`.
- **Chaining heterogeneous processors**: `ProcessorChain<WaveShaper<...>, ProcessorDuplicator<Filter, FilterCoefs>, Convolution>` — an IIR filter must be wrapped in `ProcessorDuplicator` because `IIR::Filter` alone doesn't support stereo.

## Code Examples
```cpp
// three waveshaping transfer functions
float relu(float x) { return std::max(0.0f, x); }
float sigmoid(float x) { return 1.0f / (1.0f + std::exp(-x)); }
float clip(float input, float clip_value) {
    if (std::abs(input) > clip_value) return (input < 0) ? -1.0f : 1.0f;
    return input;
}
```
```cpp
// parameterized clip lambda, reading a live plugin parameter
juce::dsp::ProcessorChain<juce::dsp::WaveShaper<float, std::function<float(float)>>> processorChain;
// constructor:
addParameter(clipThreshold = new juce::AudioParameterFloat("clipThresh", "Clip threshold", 0.0f, 1.0f, 0.1f));
auto& waveshaper = processorChain.template get<0>();
waveshaper.functionToUse = [this](float x) {
    float clip = this->clipThreshold->get();
    if (std::abs(x) > clip) return (x < 0) ? -1.0f : 1.0f;
    return x;
};
```
```cpp
// a 3-stage amp emulator chain: waveshaper -> stereo IIR filter -> convolution
using Filter = juce::dsp::IIR::Filter<float>;
using FilterCoefs = juce::dsp::IIR::Coefficients<float>;
juce::dsp::ProcessorChain<
    juce::dsp::WaveShaper<float, std::function<float(float)>>,       // pre-amp distortion
    juce::dsp::ProcessorDuplicator<Filter, FilterCoefs>,              // tone stage (stereo IIR)
    juce::dsp::Convolution                                            // speaker cabinet (FIR)
> processorChain;
```
- **What it demonstrates**: the DSP-Trinity-to-plugin pipeline scales from "one processor" (Ch.28-29) to a heterogeneous multi-stage chain simply by listing more types in `ProcessorChain<...>`.

## Anti-patterns
- Using the default (capture-less) `WaveShaper<float>` when the transfer function needs to read a live plugin parameter — it silently can't; switch to the `std::function<float(float)>` template parameter and capture `this`.
- Forgetting `ProcessorDuplicator` when adding an IIR filter to a chain that also has stereo-native processors (WaveShaper, Convolution) — `IIR::Filter` alone is mono-only.

## Key Takeaways
1. Waveshaping = one nonlinear function applied per-sample; ReLU/sigmoid/clip give qualitatively different distortion characters.
2. A guitar amp is a chain of exactly the 3 DSP Trinity members: waveshaper (distortion stages) + IIR (tone/EQ stages) + FIR/convolution (speaker cabinet impulse response) — this classical-DSP chain is what neural modeling (Ch.31+) targets replacing wholesale or augmenting.
3. `std::function<float(float)>` as the WaveShaper's function type (instead of the default) is required to let its lambda capture `this` and read live parameters.
4. `ProcessorDuplicator<Filter, FilterCoefs>` is the standard fix for adding a mono-only IIR filter into an otherwise-stereo processor chain.

## Connects To
- **Ch 27-29**: FIR/IIR, the other two DSP Trinity members combined here with waveshaping.
- **Ch 31**: pivots from this classical DSP amp model to neural-network-based amp emulation, motivated by exactly the non-linearity this chapter's waveshapers hand-model.
