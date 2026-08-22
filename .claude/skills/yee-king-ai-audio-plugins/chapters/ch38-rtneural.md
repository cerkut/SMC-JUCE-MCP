# Chapter 38: Faster LSTM using RTNeural

## Core Idea
Introduces **RTNeural** (Jatin Chowdhury, 2021) — a header-only, C++, inference-only neural network library — as a 2-3x faster alternative to TorchScript for real-time deployment, verified bit-identical against a TorchScript model with the same weights, then deployed in a mono JUCE plugin with dramatically simpler `processBlock` code (at the cost of more verbose weight-loading setup).

## Frameworks Introduced
- **RTNeural**: a real-time-safe, header-only C++ inference library implementing common layer types (LSTM, Dense, convolutional, etc.) efficiently and *visibly to the compiler* (enabling further optimization) — but **inference only**, no training support. Models are defined at compile time via C++ templates (`RTNeural::ModelT<...>`), and weights are loaded at runtime from a JSON file exported from the trained PyTorch model.
- **`save_for_rtneural`**: a `SimpleLSTM` method (from Ch.35) that exports trained weights to a JSON dictionary (one array per layer's parameters) — the bridge format between PyTorch training and RTNeural inference.

## Key Concepts
- **Compile-time model definition**: `RTNeural::ModelT<float, 1, 1, RTNeural::LSTMLayerT<float, 1, lstm_units>, RTNeural::DenseT<float, lstm_units, 1>>` — the `1, 1` are input/output width; the layer list mirrors the PyTorch model's own layer sequence exactly (LSTM → Dense), and unit counts must match the exported JSON or a runtime sanity-check should catch the mismatch.
- **`model.get<0>()` / `model.get<1>()`**: index into the compile-time-defined layer stack to access each layer for weight-loading, mirroring the `processorChain.get<N>()` pattern from Ch.28-30's JUCE DSP chains.
- **`RTNeural::torch_helpers::loadLSTM<float>(json, "lstm.", layer)` / `loadDense<float>(json, "dense.", layer)`**: load a named layer's weights out of the exported JSON directly into an RTNeural layer object.
- **Output parity verified**: running the same weights through both TorchScript and RTNeural gives bit-identical output (`RT: 0.085324 TS: 0.085324` etc.) — confirms RTNeural is a faithful reimplementation, not an approximation.
- **Per-sample inference API**: `lstmModel.forward(&inData[i])` — RTNeural processes one sample at a time (no batch/block tensor plumbing needed), dramatically simplifying `processBlock` compared to TorchScript's tensor-shape juggling (Ch.32-33, 37).
- **RTNeural's limitations**: only a subset of torch's layer types are implemented, and its speed advantage over TorchScript *shrinks* as network size grows.

## Code Examples
```cpp
// defining an RTNeural model architecture (compile-time)
const int lstm_units = 64;
using MyLSTMType = RTNeural::ModelT<float, 1, 1,
    RTNeural::LSTMLayerT<float, 1, lstm_units>,
    RTNeural::DenseT<float, lstm_units, 1>>;
```
```cpp
// loading weights from an exported JSON file
MyLSTMType model;
std::ifstream jsonStream("lstm_weights.json", std::ifstream::binary);
nlohmann::json modelJson; jsonStream >> modelJson;

auto& lstm = model.get<0>();
RTNeural::torch_helpers::loadLSTM<float>(modelJson, "lstm.", lstm);
auto& dense = model.get<1>();
RTNeural::torch_helpers::loadDense<float>(modelJson, "dense.", dense);
```
```cpp
// JUCE plugin: setup with a sanity-checked weight load
using RTLSTMModel32 = RTNeural::ModelT<float, 1, 1,
    RTNeural::LSTMLayerT<float, 1, 32>, RTNeural::DenseT<float, 32, 1>>;
RTLSTMModel32 lstmModel;

void setupModel(RTLSTMModel32& model, std::string jsonFile) {
    int lstm_units = 32;
    std::ifstream jsonStream(jsonFile, std::ifstream::binary);
    nlohmann::json modelJson; jsonStream >> modelJson;
    auto& lstm = model.get<0>();
    const int json_lstm_size = modelJson["lstm.weight_ih_l0"].size() / 4;
    if (json_lstm_size != lstm_units) throw std::exception();  // fail loudly on mismatch
    RTNeural::torch_helpers::loadLSTM<float>(modelJson, "lstm.", lstm);
    auto& dense = model.get<1>();
    RTNeural::torch_helpers::loadDense<float>(modelJson, "dense.", dense);
}
```
```cpp
// processBlock: dramatically simpler than TorchScript (Ch.37) - no tensor shape juggling
for (int channel = 0; channel < totalNumInputChannels; ++channel) {
    auto* outData = buffer.getWritePointer(channel);
    auto* inData  = buffer.getReadPointer(channel);
    for (auto i = 0; i < buffer.getNumSamples(); ++i) {
        outData[i] = lstmModel.forward(&inData[i]);   // per-sample, no tensors
    }
}
```
- **What it demonstrates**: RTNeural trades verbose weight-loading setup for a dramatically simpler real-time processing path — the exact inverse trade-off from TorchScript.

## Anti-patterns
- Assuming RTNeural is always faster — its speed advantage over TorchScript *shrinks* as the network grows; benchmark at your actual target size.
- Mismatching the compile-time model architecture (unit counts, layer order) against the exported JSON without a sanity check — the book explicitly checks `json_lstm_size != lstm_units` and throws rather than silently loading garbage weights.
- Reaching for RTNeural when you need a torch module type it doesn't implement — check coverage first; RTNeural only supports a subset of torch's layer types.

## Key Takeaways
1. RTNeural = header-only, compile-time-templated, inference-only C++ library; 2-3x faster than TorchScript, verified bit-identical output on matching weights.
2. Workflow: train in PyTorch (as before) → `save_for_rtneural` exports JSON → define matching `ModelT<...>` architecture in C++ → `loadLSTM`/`loadDense` populate weights → per-sample `forward()` calls in `processBlock`.
3. The trade-off vs. TorchScript: much simpler/faster real-time processing code, at the cost of more explicit (and architecture-must-match-exactly) weight-loading setup.
4. Directly relevant to any "should I use TorchScript or RTNeural" decision (e.g. this project's own libtorch/Apple-Silicon note): RTNeural sidesteps the entire libtorch runtime dependency and its platform-support gaps, at the cost of losing training capability and some torch layer types.

## Connects To
- **Ch 32-33, 37**: the TorchScript-based pipeline RTNeural is offered as a faster, leaner alternative to.
- **Ch 35**: `save_for_rtneural`, a `SimpleLSTM` method introduced there and used properly here.
- This project's own libtorch/Apple-Silicon TODO note: RTNeural is the concrete "avoid libtorch's platform gaps entirely" alternative referenced in the TorchScript-Alternatives wiki.
