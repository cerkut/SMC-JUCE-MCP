# Chapter 14: Untrained torchknob

## Core Idea
Replaces the superknob's hand-coded linear interpolation with an actual (untrained) `torch::nn::Linear` layer wrapped in a reusable `NeuralNetwork` class, then normalizes its output with a softmax layer — establishing the JUCE↔libtorch separation pattern used for the rest of the book.

## Frameworks Introduced
- **The `NeuralNetwork` wrapper class pattern**: a class inheriting `torch::nn::Module` that exposes a **plain-vector** public API (`forward(vector<float>) -> vector<float>`, `addTrainingData`, `runTraining`) while hiding all `torch::Tensor` plumbing behind a private `forward(Tensor&) -> Tensor`. This keeps JUCE UI code libtorch-agnostic — a design decision repeated in every later neural-controlled plugin.
- **`register_module`**: how layers (e.g. `linear`, `softmax`) get registered with the parent `torch::nn::Module` so it can track/traverse them.

## Key Concepts
- **Two-tier `forward`**: public `forward(vector<float>)` converts to a tensor, calls the private tensor-based `forward(Tensor&)`, converts back to a vector — isolates all tensor code in one place.
- **Softmax normalization**: `torch::nn::Softmax(1)` forces a layer's output along dimension 1 to sum to 1 — used here to force the two slider-target outputs into a predictable, boundable range.
- **Lightweight CMake unit testing**: a second `add_executable` target (e.g. `test_nn`) linking only the class under test + libtorch, so iterating on network code doesn't require a full JUCE rebuild each time.

## Code Examples
```cpp
// NeuralNetwork.h — the "aspirational" header pattern
class NeuralNetwork : torch::nn::Module {
public:
    NeuralNetwork(int64_t n_inputs, int64_t n_outputs);
    std::vector<float> forward(const std::vector<float>& inputs);
    void addTrainingData(std::vector<float> inputs, std::vector<float> outputs);
    void runTraining(int epochs);
private:
    int64_t n_inputs;
    int64_t n_outputs;
    torch::nn::Linear linear{nullptr};
    torch::nn::Softmax softmax{nullptr};
    torch::Tensor forward(const torch::Tensor& input);
};
```
```cpp
// constructor: register_module wires layers into the parent Module
NeuralNetwork::NeuralNetwork(int64_t _n_inputs, int64_t _n_outputs)
    : n_inputs{_n_inputs}, n_outputs{_n_outputs} {
    linear  = register_module("linear",  torch::nn::Linear(n_inputs, n_outputs));
    softmax = register_module("softmax", torch::nn::Softmax(1));
}

// private tensor-level forward: linear -> softmax
torch::Tensor NeuralNetwork::forward(const torch::Tensor& input) {
    torch::Tensor out = linear(input);
    out = softmax(out);
    return out;
}

// public vector-level forward: hides all tensor plumbing from callers
std::vector<float> NeuralNetwork::forward(std::vector<float> inputs) {
    torch::Tensor in_t = torch::empty({1, n_inputs});
    for (long i = 0; i < n_inputs; ++i) in_t[0][i] = inputs[i];
    torch::Tensor out_t = forward(in_t);
    std::vector<float> outputs(n_outputs);
    for (long i = 0; i < n_outputs; ++i) outputs[i] = out_t[0][i].item<float>();
    return outputs;
}
```
```cmake
# a second, lightweight test executable alongside the plugin target
add_executable(test_nn src/NeuralNetwork.cpp src/test_nn.cpp)
target_link_libraries(test_nn "${TORCH_LIBRARIES}")
set_property(TARGET test_nn PROPERTY CXX_STANDARD 14)
```
- **What it demonstrates**: the vector-in/vector-out public API + tensor-only private API split; a fast unit-test target separate from the full plugin build.

## Anti-patterns
- Letting `torch::Tensor` types leak into JUCE UI code — couples UI logic to libtorch unnecessarily; keep the public API in plain vectors/floats.
- Rebuilding the whole JUCE plugin to test small neural-net logic changes — add a lightweight second CMake executable target instead.
- Expecting an *untrained* network's output to be usable directly — random initial weights mean outputs may be out-of-range or barely move the target sliders at all; this is expected and fixed by training (Ch.15).

## Key Takeaways
1. Wrap libtorch entirely inside a `NeuralNetwork` class with a plain-vector public interface — never expose `torch::Tensor` to UI code.
2. `register_module` is required for every layer so the parent `Module` can track it (needed later for saving/training).
3. Softmax forces outputs to sum to 1 — useful for normalization, but (as Ch.15 reveals) wrong for *independent* parameter mapping.
4. Add a second, minimal CMake executable target to unit-test network logic without a full plugin rebuild.

## Connects To
- **Ch 13**: this replaces the superknob's hand-written interpolation with an actual (still untrained) neural net.
- **Ch 15**: trains this exact network and specifically reverts softmax → sigmoid because independent parameters shouldn't be forced to sum to 1.
