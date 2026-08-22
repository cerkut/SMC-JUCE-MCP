# Chapter 8: Basic plugin development

## Core Idea
Builds a minimal JUCE sine-wave synth plugin end-to-end: `processBlock`, a UI slider bound via `Slider::Listener`, and MIDI note-on handling — the foundational plugin pattern every later chapter extends.

## Key Concepts
- **`processBlock(AudioBuffer<float>&, MidiBuffer&)`**: called repeatedly by the host; a synth ignores incoming audio and writes new samples, an effect reads/modifies the buffer in place. Must run fast — under-running causes audio dropouts.
- **`dphase`**: phase increment per sample — `(2π / sampleRate) * frequency`; doubling frequency doubles `dphase`.
- **`Slider::Listener` pattern**: (1) declare the slider member, (2) `addAndMakeVisible` + `setBounds` in the editor, (3) inherit `Slider::Listener` and override `sliderValueChanged`, (4) `addListener(this)` — then editor calls a public processor method (e.g. `updateFrequency`) to cross from UI-thread to the actual synthesis state.
- **`acceptsMidi()`**: driven by the `NEEDS_MIDI_INPUT` CMakeLists.txt flag (ch.4), not hand-edited directly.
- **`juce::ScopedNoDenormals`**: prevents tiny floating-point values (denormals) from silently degrading performance — standard boilerplate at the top of every `processBlock`.

## Code Examples
```cpp
// phase-increment calculation
double TestPluginAudioProcessor::getDPhase(double freq, double sampleRate) {
    double two_pi = 3.1415927 * 2;
    return (two_pi / sampleRate) * freq;
}

// sine generation inside processBlock (channel 0 only)
for (int channel = 0; channel < totalNumOutputChannels; ++channel) {
    if (channel == 0) {
        auto* channelData = buffer.getWritePointer(channel);
        int numSamples = buffer.getNumSamples();
        for (int sInd = 0; sInd < numSamples; ++sInd) {
            channelData[sInd] = (float)(std::sin(phase) * 0.25);
            phase += dphase;
        }
    }
}

// MIDI note-on -> frequency
for (const auto metadata : midiMessages) {
    auto message = metadata.getMessage();
    if (message.isNoteOn()) {
        updateFrequency(juce::MidiMessage::getMidiNoteInHertz(message.getNoteNumber()));
        break;
    }
}
```
- **What it demonstrates**: the three recurring plugin building blocks — audio synthesis in `processBlock`, UI-to-processor communication via a public setter, MIDI parsing via `isNoteOn()`/`getMidiNoteInHertz()`.

## Anti-patterns
- Doing slow work inside `processBlock` — it must keep up with the host's continuous audio-block stream or you get dropouts.
- Editing `acceptsMidi()` by hand instead of the `NEEDS_MIDI_INPUT` CMakeLists.txt flag — works, but isn't "the polite JUCE way" and can drift out of sync with the build config.

## Key Takeaways
1. `processBlock` is the one function almost every later chapter revisits — synths write to it, effects transform it, ML-driven plugins read parameters set from it.
2. UI → processor communication always goes through a public method call from the editor to the processor (`audioProcessor.updateFrequency(...)`), not shared mutable state.
3. MIDI note-to-frequency conversion is one line: `juce::MidiMessage::getMidiNoteInHertz(noteNumber)`.

## Connects To
- **Ch 9**: adds a second oscillator (FM synthesis) on top of this exact sine-plugin skeleton.
- **Ch 13**: reuses this same FM-plugin-plus-slider pattern as the base for the Superknob.
