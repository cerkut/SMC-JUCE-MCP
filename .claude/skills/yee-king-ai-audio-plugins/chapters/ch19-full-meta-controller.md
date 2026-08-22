# Chapter 19: From plugin host to meta-controller

## Core Idea
Completes the meta-controller by querying an *arbitrary* hosted plugin's parameter list at load time, sizing the neural network's output to match, and wiring the torchknob's trained output back into `setParameter` calls on the hosted plugin — the payoff chapter for the entire Part 2 arc.

## Frameworks Introduced
- **Dynamic network sizing from plugin introspection**: `NeuralNetwork(1, countValidParameters())` — the network's output width is *derived at runtime* from whatever plugin gets loaded, not fixed at compile time like the earlier FM-synth-specific torchknob.

## Key Concepts
- **`getParameters()` + filtering**: `pluginNode->getProcessor()->getParameters()` returns every parameter, including JUCE's auto-added `MIDI CC` control parameters — these must be filtered out (`!p->getName(100).contains("MIDI CC")`) to get the plugin's "real" parameters.
- **Read/write parameter symmetry**: `getHostedPluginParamValues()` (read all real params into a `vector<float>`) and `setHostedPluginParamValues(vector<float>)` (write them back via `setParameter(index, value)`) are mirror-image functions using the same filtered iteration.
- **Where the `NeuralNetwork` lives**: in the `PluginEditor` (not the processor) — because the editor is what receives torchknob movements and needs direct access to train/infer.

## Code Examples
```cpp
// filtering out JUCE's auto-added MIDI CC parameters
for (const juce::AudioProcessorParameter* p : params) {
    if (!p->getName(100).contains("MIDI CC")) {
        DBG("p: " << p->getName(100) << " : " << p->getValue());
    }
}
```
```cpp
// after loading a plugin, size the network to its (filtered) parameter count
this->audioProcessor.loadPlugin(chooser.getResult());
this->nn = NeuralNetwork(1, this->audioProcessor.countValidParameters());
```
```cpp
// one training example: torchknob position -> current plugin parameter snapshot
nn.addTrainingData(
    {(float) superKnobTrain.getValue()},
    this->audioProcessor.getHostedPluginParamValues());
```
```cpp
// writing inferred values back onto the plugin (setParameter is deprecated but simplest)
void PluginHostProcessor::setHostedPluginParamValues(std::vector<float> values) {
    int pind{0};
    if (pluginNode) {
        auto params = pluginNode->getProcessor()->getParameters();
        for (const auto* p : params) {
            if (!p->getName(100).contains("MIDI CC")) {
                pluginNode->getProcessor()->setParameter(pind, values[pind]);
                pind++;
            }
        }
    }
}
```
- **What it demonstrates**: the full "any plugin, any parameter count" generalization of the torchknob idea from Ch.13-15 — no more hardcoded 2-parameter mapping.

## Anti-patterns
- Forgetting to filter out JUCE's auto-injected `MIDI CC` parameters when building a training vector — they will silently pollute the parameter count/order and desync from the plugin's real controls.
- Using the deprecated `setParameter(index, value)` API long-term — JUCE's recommended replacement is `AudioProcessorParameter`/`AudioProcessorParameterGroup`, but the book keeps `setParameter` for simplicity.

## Key Takeaways
1. The meta-controller's neural net is sized dynamically from `countValidParameters()` — this is what makes it work with *any* loaded plugin, not just the book's FM synth.
2. Every parameter-touching function (print/count/get/set) must apply the same `MIDI CC` filter consistently, or indices desync between reading and writing.
3. Training examples are (torchknob value) → (full snapshot of all filtered plugin parameters) pairs — morphing between presets is just interpolation through this learned mapping.
4. Listed extensions (auto-populate training data from presets, XY-pad input, multi-synth hosting, spectral/video feature input) mark where a reader would go next.

## Connects To
- **Ch 12-15**: this is the "any synth" generalization of the fixed-FM-synth torchknob.
- **Ch 16-18**: the plugin-hosting graph and UI-window mechanisms this chapter drives with the trained network's output.
- Part 3/4 (Improviser, Neural FX): the book's next two independent example tracks, unrelated to the meta-controller but sharing the same Part 1 setup.
