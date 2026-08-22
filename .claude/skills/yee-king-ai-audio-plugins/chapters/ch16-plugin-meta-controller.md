# Chapter 16: Plugin meta-controller

## Core Idea
Strips the FM synthesizer's own synthesis code out of the torchknob plugin and replaces it with **plugin-hosting** code — loading and running a *different*, arbitrary VST3 plugin from disk and forwarding MIDI/audio to it. This converts a fixed-synth torchknob into a plugin host that can control anything.

## Key Concepts
- **`AudioPluginFormatManager`**: enumerates supported plugin formats (VST3, AU, etc.) — `addDefaultFormats()` registers the built-in ones; loop `getFormats()` to find the index for a specific format (e.g. "VST3").
- **`KnownPluginList`**: despite the name, a *manager* — not the list itself. The actual list is an `OwnedArray<PluginDescription>` it populates via `scanAndAddFile`.
- **`AudioPluginInstance`**: the loaded plugin, held via `std::unique_ptr` once `createPluginInstance` succeeds.
- **`suspendProcessing(true/false)`**: must wrap plugin (re)loading so `processBlock` isn't called mid-load.
- **Loading location matters**: `loadPlugin` must be called from `prepareToPlay`, not the constructor — the constructor doesn't yet know sample rate/block size, both required by `createPluginInstance`.

## Code Examples
```cpp
// find the VST3 format index (once, in the constructor)
pluginFormatManager.addDefaultFormats();
int currInd{0};
for (const juce::AudioPluginFormat* f : pluginFormatManager.getFormats()) {
    if (f->getName() == "VST3") { vstFormatInd = currInd; break; }
    currInd++;
}
```
```cpp
// loadPlugin: scan a file, then instantiate it
void PluginHostProcessor::loadPlugin(const juce::File& pluginFile) {
    suspendProcessing(true);
    pluginDescriptions.clear();
    bool added = knownPluginList.scanAndAddFile(
        pluginFile.getFullPathName(), true, pluginDescriptions,
        *pluginFormatManager.getFormat(vstFormatInd));

    juce::String errorMsg{""};
    pluginInstance = pluginFormatManager.createPluginInstance(
        *pluginDescriptions[0], getSampleRate(), getBlockSize(), errorMsg);
    pluginInstance->enableAllBuses();
    pluginInstance->prepareToPlay(getSampleRate(), getBlockSize());
    suspendProcessing(false);
}
```
```cpp
// processBlock: forward MIDI from the on-screen keyboard, then delegate to the hosted plugin
if (midiToProcess.getNumEvents() > 0) {
    midiMessages.addEvents(midiToProcess, midiToProcess.getFirstEventTime(),
                            midiToProcess.getLastEventTime() + 1, 0);
    midiToProcess.clear();
}
if (pluginInstance) {
    pluginInstance->processBlock(buffer, midiMessages);
}
```
- **What it demonstrates**: the minimal "load an arbitrary VST3 and run its `processBlock`" pattern — the entire mechanism a plugin host needs.

## Anti-patterns
- Calling `loadPlugin` from the constructor instead of `prepareToPlay` — sample rate/block size aren't known yet at construction time.
- Calling `processBlock` on the host while a plugin load is in progress — always bracket loading with `suspendProcessing(true/false)`.

## Key Takeaways
1. Hosting a plugin is: enumerate formats → scan a file into a `PluginDescription` → `createPluginInstance` → `prepareToPlay` → forward `processBlock` calls.
2. `suspendProcessing` must wrap any plugin (re)load to avoid racing the audio thread.
3. The torchknob's neural-net UI code (superknob, training button) survives this refactor untouched — only the *target* of its output changes from hardcoded synth params to an arbitrary hosted plugin.

## Connects To
- **Ch 9, 13-15**: the torchknob code being generalized here.
- **Ch 17**: replaces this single hardcoded plugin slot with a full `AudioProcessorGraph` for multiple hosted plugins.
- **Ch 19**: connects this hosting mechanism back to the trained neural network to complete the meta-controller.
