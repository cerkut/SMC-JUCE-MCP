# Chapter 33: JUCE LSTM plugin

## Core Idea
Solves the critical bug that block-based LSTM processing resets state every block (causing audible discontinuities), by re-tracing the TorchScript model to accept/return an explicit `(h0, c0)` state tuple, then wraps the whole state-carrying pipeline in a real JUCE plugin.

## Frameworks Introduced
- **The `LSTMState` type**: `typedef c10::intrusive_ptr<c10::ivalue::Tuple> LSTMState;` — libtorch's (undocumented at time of writing) representation of an LSTM's `(hidden_state, cell_state)` pair, needed to carry state between block-based `forward()` calls.

## Key Concepts
- **Why block-based processing glitches**: passing `[0.5]` then `[0.1]` as two separate `forward()` calls gives a *different* result than passing `[[0.5],[0.1]]` as one sequence — because each `forward()` call resets internal state at its end unless you explicitly capture and re-feed it. Audibly, this is small discontinuities at every block boundary.
- **Tracing a state-aware TorchScript model**: the original `torch.jit.trace(model, (input,))` only accepts an input tensor — calling it with a state argument crashes ("expected at most 2 arguments"). Fix: re-trace with `torch.jit.trace(model, (input, (h0, c0)))` so the traced graph itself accepts and returns state.
- **`c10`/"Caffe2" naming**: `c10::intrusive_ptr` is a lighter-weight smart pointer than `shared_ptr` (offloads reference counting to the wrapped object instead of a separate control block) — used because LSTM state must be passed through TorchScript's generic `IValue` interface.

## Code Examples
```python
# demonstrating the state bug, then the fix
my_lstm = torch.nn.LSTM(1, 1, 1)
# WITHOUT state carried forward: 0.1 after 0.5 gives a different result
# than 0.1 processed alone or as part of one sequence.
output, state = my_lstm.forward(torch.tensor([[0.5]]))
output, state = my_lstm.forward(torch.tensor([[0.1]]), state)  # <-- pass state back in
```
```python
# tracing a model that accepts a state argument
h0 = torch.rand(num_layers, hidden_size)
c0 = torch.rand(num_layers, hidden_size)
traced_lstm = torch.jit.trace(my_lstm, (input, (h0, c0)))
traced_lstm.save('my_lstm.pt')
```
```cpp
// C++: creating an initial random state
typedef c10::intrusive_ptr<c10::ivalue::Tuple> LSTMState;
LSTMState getRandomStartState(int numLayers, int hiddenSize) {
    torch::Tensor h0 = torch::randn({numLayers, hiddenSize});
    torch::Tensor c0 = torch::randn({numLayers, hiddenSize});
    return c10::ivalue::Tuple::create({h0, c0});
}

// C++: block processing that both consumes AND returns state
LSTMState processBlockState(torch::jit::script::Module& model, const LSTMState& state,
                              std::vector<float>& inBlock, std::vector<float>& outBlock, int numSamples) {
    torch::Tensor in_t = torch::from_blob(inBlock.data(), {(int64_t)numSamples}).view({-1, 1});
    std::vector<torch::jit::IValue> inputs;
    inputs.push_back(in_t);
    inputs.push_back(state);                       // <-- state goes in as a second IValue

    torch::jit::IValue out_ival = model.forward(inputs);
    auto out_elements = out_ival.toTuple()->elements();
    torch::Tensor out_t = out_elements[0].toTensor().view({-1});
    float* data_ptr = out_t.data_ptr<float>();
    std::copy(data_ptr, data_ptr + inBlock.size(), outBlock.begin());

    return out_elements[1].toTuple();               // <-- state comes back out, feed into next call
}
```
```cpp
// JUCE plugin setup: mono I/O, model + state as processor members
torch::jit::script::Module lstmModel;
LSTMState lstmState;
// constructor:
lstmModel = torch::jit::load("path/to/my_lstm_with_state.pt");
lstmState = getRandomStartState(1, 1);
// bus layout: .withInput("Input", juce::AudioChannelSet::mono(), true)
//             .withOutput("Output", juce::AudioChannelSet::mono(), true)
```
- **What it demonstrates**: the full fix for the state-reset bug — retrace with state args in Python, carry a `LSTMState` handle in C++, thread it through every `processBlockState` call, storing the returned state for the *next* call.

## Anti-patterns
- Processing audio in blocks without carrying LSTM state between calls — produces audible discontinuities at every block boundary, since each `forward()` call otherwise resets the model's internal memory.
- Tracing a TorchScript model without a state argument, then trying to pass state to it later — crashes with an argument-count mismatch; the state-accepting signature must be baked in at trace time.
- Allocating buffers inside the real-time audio loop — the chapter explicitly flags wanting to avoid mid-loop memory allocation, especially since the TorchScript model's internal memory behavior is opaque from the C++ side.

## Key Takeaways
1. LSTM state MUST be explicitly threaded between block-based `forward()` calls (state out → state in) or you get audible glitches at block boundaries.
2. A TorchScript model must be traced *with* a state argument present for it to accept one later — this can't be retrofitted onto a state-less trace.
3. `LSTMState` (`c10::intrusive_ptr<c10::ivalue::Tuple>`) wraps `(h0, c0)` and is the type threaded through `processBlockState`'s parameter and return value.
4. This plugin is deliberately built with an *untrained* (random) LSTM first — training happens in the next several chapters; the plumbing comes first.

## Connects To
- **Ch 32**: the state-less WAV-processing pipeline this chapter fixes for real-time block-based use.
- **Ch 34-37**: train the actual LSTM this plugin's plumbing will host.
- **Ch 37**: revisits and finalizes this exact plugin once a properly trained model is available.
