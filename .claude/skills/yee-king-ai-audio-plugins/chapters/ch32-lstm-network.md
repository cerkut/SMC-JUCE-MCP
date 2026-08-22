# Chapter 32: Neural FX: LSTM network

## Core Idea
Introduces `torch.nn.LSTM` in Python, shows an *untrained* LSTM already introduces harmonic distortion (a "pinched" sine wave — free non-linearity), then exports via **TorchScript** and imports into C++/libtorch, processes a WAV file end-to-end, and benchmarks LSTM size vs. real-time feasibility. This chapter's export/import pipeline is reused by every later LSTM chapter.

## Frameworks Introduced
- **Train-in-Python, infer-in-C++ workflow** (contrasted with the meta-controller's train-in-C++ approach from Part 2): Python is faster to prototype in, has better plotting, and gives easy GPU access for training; but end users of a guitar amp emulator plugin don't need to train it themselves, so training can happen once, offline, in Python.
- **TorchScript**: the interchange format bridging Python's PyTorch and C++'s libtorch. `torch.jit.trace(model, example_input)` traces the model's execution, `.save('model.pt')` writes a portable file both environments can load.

## Key Concepts
- **LSTM hidden state (`hx`)**: like a delay effect — after passing a value in, the LSTM retains state that influences its response to the *next* input. You can choose to carry this state forward or reset it between calls.
- **An untrained LSTM already distorts**: passing a sine wave through `torch.nn.LSTM(1,1,1)` with *random, untrained* weights measurably reshapes the waveform (pinches the low point, widens the high point) and adds harmonics — evidence that even minimal LSTM structure introduces the kind of non-linear coloration a valve amp produces, before any training happens.
- **LSTM parameter count is non-linear in unit count**: 1 unit = 16 params, 2 = 40, 3 = 72, 4 = 112 — each internal parameter interacts with several others, so parameter count doesn't scale linearly with hidden-layer size.
- **`torch::NoGradGuard nograd;`**: disables gradient computation for inference-only code — measurably speeds up Windows/macOS libtorch (no measurable effect on the author's Linux machine).
- **IValue**: TorchScript's generic wrapper type for passing tensors into/out of an imported `torch::jit::script::Module` — `forward()` takes a `vector<IValue>` and returns a single `IValue` (sometimes itself a tuple to unpack).

## Code Examples
```python
# minimal LSTM pass-through in Python
import torch
torch.manual_seed(10)
my_lstm = torch.nn.LSTM(1, 1, 1)
in_t = torch.tensor([[1.0]])
out_t, hx = my_lstm.forward(in_t)
```
```python
# export via TorchScript
traced_lstm = torch.jit.trace(my_lstm, torch.rand(1, 1))
traced_lstm.save('my_lstm.pt')
```
```cpp
// import and run in C++
torch::jit::script::Module my_lstm = torch::jit::load("../my_lstm.pt");
torch::Tensor in_t = torch::zeros({10, 1});
in_t[0][0] = 1.0;
std::vector<torch::jit::IValue> inputs;
inputs.push_back(in_t);
torch::jit::IValue out_ival = my_lstm.forward(inputs);
```
```cpp
// full WAV -> LSTM -> WAV pipeline
std::vector<float> signal = myk_tiny::loadWav("mywav.wav");
torch::Tensor in_t = torch::from_blob(signal.data(), {(int64_t)signal.size()});
in_t = in_t.view({-1, 1});                          // reshape to [[x],[x],...]
std::vector<torch::jit::IValue> inputs; inputs.push_back(in_t);

torch::jit::IValue out_ival = my_lstm.forward(inputs);
auto out_elements = out_ival.toTuple()->elements();  // TorchScript LSTM returns a tuple
torch::Tensor out_t = out_elements[0].toTensor().view({-1});
float* data_ptr = out_t.data_ptr<float>();
std::vector<float> data_vector(data_ptr, data_ptr + out_t.numel());
myk_tiny::saveWav(data_vector, 1, 44100, "test.wav");
```
- **What it demonstrates**: the complete data-shape journey (vector → tensor → reshaped tensor → IValue → model → IValue-tuple → tensor → vector) that every later LSTM-in-C++ chapter repeats, and the memory-efficiency care (`from_blob` avoids copying) applied at both ends.

## Reference Tables
| LSTM hidden units | Parameters | Real-time capable? (per-platform, from performance test) |
|---|---|---|
| 1 | 16 | yes (all platforms) |
| 2 | 40 | yes |
| ... | non-linear growth | ... |
| 128 | — | Mac M1 real-time ceiling |
| 256 | — | Linux (Intel) real-time ceiling |

## Anti-patterns
- Leaving gradient computation enabled during inference-only code — wastes CPU cycles for no benefit; guard with `torch::NoGradGuard`.
- Copying data unnecessarily at the Python↔C++ boundary — `torch::from_blob` (no copy) is used deliberately on both the WAV→tensor and tensor→WAV-save paths.
- Assuming model size scales predictably across platforms — the same LSTM size that's real-time on Linux may not be on macOS/Windows; benchmark per-target.

## Key Takeaways
1. TorchScript (`torch.jit.trace` → `.save()` in Python, `torch::jit::load()` in C++) is the model interchange format for the train-in-Python/infer-in-C++ workflow.
2. Even an *untrained* LSTM introduces measurable non-linear distortion — LSTMs are structurally suited to this task before any training happens.
3. `NoGradGuard` meaningfully speeds up inference on some platforms (Windows/macOS) but not others (Linux, in this author's testing) — benchmark, don't assume.
4. Real-time feasibility caps out around 128-256 hidden units depending on platform — this directly motivates Ch.38's RTNeural as a faster alternative.

## Connects To
- **Ch 31**: the training theory this chapter's export/import mechanics will eventually serve.
- **Ch 33**: takes this exact WAV-processing pipeline into a real-time JUCE plugin (block-based, with state retention across blocks).
- **Ch 34-37**: the training side (Python dataset/model/loss/training-loop) that produces the `.pt` files this chapter's import code consumes.
- **Ch 38**: RTNeural as a 2-3x faster alternative once TorchScript's performance ceiling becomes limiting.
