# Chapter 17: Placing plugins in an AudioProcessGraph structure

## Core Idea
Upgrades the single-plugin host into a proper `AudioProcessorGraph`: audio/MIDI I/O nodes plus a plugin node, wired together with explicit `addConnection` calls, exactly mirroring how JUCE's own `AudioPluginHost` works internally.

## Key Concepts
- **Processor vs. Node**: an `AudioPluginInstance` (or `AudioGraphIOProcessor`) is the actual processing unit; a `Node::Ptr` wraps it inside the graph. You create the processor, then `addNode(std::move(processor))` hands ownership to the graph, which returns a `Node::Ptr` handle.
- **`std::move` + `unique_ptr`**: a unique_ptr only ever has one owner; `std::move` transfers ownership (e.g. from a local variable into the graph's node) — after the move, the original variable can no longer be used.
- **Two ways to construct a `unique_ptr`**: `std::make_unique<T>(...)` (preferred, used for processors) vs. `std::unique_ptr<T>{new T(...)}` (used for `audioProcGraph` itself, via constructor initializer list).
- **`addConnection({{srcNodeID, channel}, {dstNodeID, channel}})`**: wires two nodes' channels together — audio channels 0/1, or `AudioProcessorGraph::midiChannelIndex` for MIDI.
- **Cross-platform plugin file picking**: macOS/Linux VST3 bundles are *directories*; Windows plugins are *files* — `FileBrowserComponent` flags must differ per platform (`#ifdef JUCE_LINUX/JUCE_MAC/JUCE_WINDOWS`).

## Code Examples
```cpp
// building the graph's I/O nodes (constructor)
inputProc = std::make_unique<juce::AudioProcessorGraph::AudioGraphIOProcessor>(
    juce::AudioProcessorGraph::AudioGraphIOProcessor::audioInputNode);
outputProc = std::make_unique<juce::AudioProcessorGraph::AudioGraphIOProcessor>(
    juce::AudioProcessorGraph::AudioGraphIOProcessor::audioOutputNode);
midiInputProc  = std::make_unique<juce::AudioProcessorGraph::AudioGraphIOProcessor>(
    juce::AudioProcessorGraph::AudioGraphIOProcessor::midiInputNode);
midiOutputProc = std::make_unique<juce::AudioProcessorGraph::AudioGraphIOProcessor>(
    juce::AudioProcessorGraph::AudioGraphIOProcessor::midiOutputNode);

audioProcGraph->enableAllBuses();
inputNode  = audioProcGraph->addNode(std::move(inputProc));
outputNode = audioProcGraph->addNode(std::move(outputProc));
midiInNode = audioProcGraph->addNode(std::move(midiInputProc));
midiOutNode = audioProcGraph->addNode(std::move(midiOutputProc));
```
```cpp
// wiring a loaded plugin into the graph
void PluginHostProcessor::addPluginToGraph() {
    if (pluginNode) audioProcGraph->removeNode(pluginNode);
    pluginInstance->enableAllBuses();
    pluginNode = audioProcGraph->addNode(std::move(pluginInstance));

    audioProcGraph->addConnection({{pluginNode->nodeID, 0}, {outputNode->nodeID, 0}});
    audioProcGraph->addConnection({{pluginNode->nodeID, 1}, {outputNode->nodeID, 1}});
    audioProcGraph->addConnection({
        {midiInNode->nodeID, juce::AudioProcessorGraph::midiChannelIndex},
        {pluginNode->nodeID, juce::AudioProcessorGraph::midiChannelIndex}});

    pluginNode->getProcessor()->prepareToPlay(getSampleRate(), getBlockSize());
}
```
```cpp
// processBlock now delegates to the graph, not the raw plugin instance
if (pluginNode) {
    audioProcGraph->processBlock(buffer, midiMessages);
}
```
- **What it demonstrates**: the full I/O-node + plugin-node + explicit-connection wiring pattern that underlies JUCE's own `AudioPluginHost`.

## Anti-patterns
- Assuming a plugin is stereo when wiring channel 1 — the book flags this explicitly: connecting a mono plugin's channel 1 will crash.
- Hardcoding one `FileBrowserComponent` flag set across platforms — macOS/Linux need `canSelectDirectories` (plugin bundles), Windows needs `canSelectFiles`.
- Calling `enableAllBuses()`/`prepareToPlay()` directly on a raw `pluginInstance` once it's inside the graph — the graph now owns lifecycle responsibilities; call `prepareToPlay` via `pluginNode->getProcessor()` instead.

## Key Takeaways
1. A graph-based host is: I/O nodes + N plugin nodes + explicit `addConnection` calls between their channels/MIDI ports.
2. `std::move` on a `unique_ptr` transfers exclusive ownership once — the source variable becomes unusable afterward (used to hand processors into `addNode`).
3. Loading a *new* plugin means `removeNode` first if one is already present, then re-add and re-wire.
4. Plugin file-picking must branch on platform: directories on macOS/Linux, files on Windows.

## Connects To
- **Ch 16**: this graph structure generalizes the single-`pluginInstance` host from that chapter.
- **Ch 3**: mirrors exactly how JUCE's own `AudioPluginHost` app works internally.
- **Ch 19**: the meta-controller wires its trained neural-net output into this same graph structure to drive an arbitrary hosted plugin's parameters.
