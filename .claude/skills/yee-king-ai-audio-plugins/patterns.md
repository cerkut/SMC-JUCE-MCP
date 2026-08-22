# Patterns & Techniques

## The libtorch training loop (canonical form)
**When to use**: any time you need to train a neural network model in libtorch/PyTorch.
**How**: forward pass → compute loss (`mse_loss` or a custom loss) → `optimizer.zero_grad()` → `loss.backward()` → `optimizer.step()`. Repeat until loss converges (fixed epochs, or track `dLoss` and break on convergence).
**Trade-offs**: simple and universal, but naive fixed-epoch loops waste compute once converged — prefer a convergence check.
(Ch 11, 15, 34-36)

## Vector-in/vector-out neural network wrapper
**When to use**: whenever a neural network needs to be called from non-libtorch code (e.g. JUCE UI code).
**How**: wrap the model in a class exposing a public `forward(vector<float>) -> vector<float>` that internally converts to/from tensors and calls a private `forward(Tensor&) -> Tensor`.
**Trade-offs**: adds a thin conversion layer, but keeps UI/business logic completely libtorch-agnostic. (Ch 14)

## Buffer, don't touch — audio thread safety for UI-originated events
**When to use**: any time UI-thread input (MIDI, slider values) needs to reach the audio processor.
**How**: store incoming events in a buffer (`juce::MidiBuffer`, a plain queue, etc.); merge into the processor's own state only inside `processBlock`, on your own schedule.
**Trade-offs**: adds indirection, but is the only safe way to cross the UI/audio thread boundary. (Ch 16, 22)

## Scheduled note-off via a per-note timestamp array
**When to use**: generating MIDI note-on/off pairs where the off must fire on a *later* `processBlock` call.
**How**: `unsigned long noteOffTimes[127]` + a running `elapsedSamples` counter. On note-on, set `noteOffTimes[note] = elapsedSamples + durationInSamples`. Each `processBlock`, scan the array for due notes and emit their note-offs.
**Trade-offs**: buffer-granularity (not sample-accurate) timing; simple and sufficient for most use cases. (Ch 22-25)

## Graph-based plugin hosting
**When to use**: hosting one or more arbitrary plugins inside your own plugin.
**How**: `AudioProcessorGraph` + I/O nodes (`AudioGraphIOProcessor`) + plugin nodes (`addNode(std::move(pluginInstance))`) + explicit `addConnection` calls between node channels/MIDI ports.
**Trade-offs**: more setup than a single hardcoded `pluginInstance->processBlock()` call, but generalizes to any number of plugins, mirrors JUCE's own `AudioPluginHost`. (Ch 16-17)

## Dynamic parameter introspection for generic control
**When to use**: building a control system (like the meta-controller) that must work with *any* loaded plugin, not a fixed one.
**How**: `pluginNode->getProcessor()->getParameters()`, filtered to exclude JUCE's auto-added `MIDI CC` parameters; size your control system's output to match the filtered count.
**Trade-offs**: requires consistent filtering everywhere (print/count/get/set) or indices desync. (Ch 19)

## Time-domain vs. frequency-domain convolution
**When to use**: applying an impulse response to a signal (reverb, cabinet simulation, etc.).
**How**: time-domain = direct weighted-sum-and-shift (`conv()` in Ch 28), simple but real-time-feasible only up to ~25-30k coefficients. Frequency-domain = FFT both signal and IR (same length, power-of-two padded), multiply, inverse-FFT — ~100-200x faster for long IRs.
**Trade-offs**: time-domain is simpler to reason about and fine for short IRs; frequency-domain is necessary for realistic reverb tails, at the cost of padding/truncation constraints.
(Ch 28)

## Parameterized JUCE waveshaper lambda
**When to use**: a `dsp::WaveShaper` whose transfer function needs to read a live plugin parameter.
**How**: declare the chain as `WaveShaper<float, std::function<float(float)>>` (not the default capture-less function type), then set `functionToUse = [this](float x){ ... this->someParam->get() ... };`.
**Trade-offs**: slightly more verbose template signature, but enables dynamic control instead of a hardcoded transfer function. (Ch 30)

## Multi-stage `ProcessorChain` for a DSP effects rack
**When to use**: chaining heterogeneous DSP stages (e.g. waveshaper → IIR filter → convolution) to build a grey-box amp model.
**How**: `ProcessorChain<WaveShaper<...>, ProcessorDuplicator<IIR::Filter<float>, IIR::Coefficients<float>>, Convolution>` — wrap mono-only processors (like `IIR::Filter`) in `ProcessorDuplicator` to make them stereo-compatible with the rest of the chain.
**Trade-offs**: uniform `prepare`/`reset`/`process` interface across stages, but each stage's type must be explicitly compatible (stereo vs. mono). (Ch 28-30)

## LSTM state threading across audio blocks
**When to use**: running a stateful RNN/LSTM in a block-based real-time audio callback.
**How**: (1) re-trace/script the model so it explicitly accepts and returns a state tuple; (2) hold a `LSTMState` handle (or let the model manage it internally, if the model class does so); (3) pass the current state in and capture the returned state on every `processBlock` call.
**Trade-offs**: without this, you get audible discontinuities at every block boundary — the fix is mandatory for stateful real-time inference, not optional polish. (Ch 33, 37)

## Train-in-Python, infer-in-C++
**When to use**: any neural-network-in-a-plugin project where end users don't need to train the model themselves.
**How**: design/train/export in Python (fast prototyping, GPU access, TorchScript/`save_for_rtneural` export) → import and run inference-only in C++/JUCE.
**Trade-offs**: adds an export/interchange step (TorchScript or RTNeural JSON) vs. training entirely in C++ (as the meta-controller does), but is far faster to iterate on and gives GPU-accelerated training. (Ch 31-38)

## TorchScript vs. RTNeural for inference
**When to use**: choosing a runtime for a trained model in a real-time plugin.
**How**: TorchScript — full torch module coverage, simpler weight loading (`torch.jit.load` one-liner), but slower and dependent on the full libtorch runtime. RTNeural — 2-3x faster, header-only, no libtorch dependency, but inference-only, limited layer coverage, and requires the C++ model architecture to exactly match the exported JSON (with a manual sanity check).
**Trade-offs**: RTNeural's speed advantage shrinks as network size grows — benchmark at your actual target size before choosing. (Ch 32-33, 37-38)

## Variable-order Markov generation with repetition avoidance
**When to use**: generating a musical (or any) sequence from a trained Markov model without getting stuck repeating one state.
**How**: prefer the highest order with an available observation; if a state's transition row has ≤1 possible next observation, drop to a lower order and resample.
**Trade-offs**: higher order = more context-aware but sparser (risk of repetition); the fallback rule buys variety back without abandoning higher-order context when it's actually useful. (Ch 20-25)
