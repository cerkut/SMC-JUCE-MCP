# Cheatsheet

## Which DSP technique for which job?

| Need | Technique | Why |
|---|---|---|
| Model an LTI system from a captured response (reverb, cabinet) | FIR / convolution | Impulse response = coefficients, directly |
| Model a resonant/feedback system (EQ, tone stage) | IIR | Feedback lets it "ring"; needs filter design, not impulse capture |
| Model non-linear distortion (fixed, hand-designed) | Waveshaper | Cheap, deterministic, but can't learn from data |
| Model a strongly non-linear, hard-to-derive system (valve amp) | Neural network (LSTM/CNN) | Classical black-box (waveshaper/convolution) can't capture enough non-linearity |

## Which neural inference runtime?

| Need | Choice |
|---|---|
| End users train the model themselves, live, in the plugin | libtorch, train in C++ (meta-controller style) |
| Fastest possible iteration on model design + GPU training | Train in Python, export via TorchScript |
| Maximum real-time inference speed, no libtorch dependency | RTNeural (export weights to JSON, define matching C++ architecture) |
| Need full torch module coverage in the deployed model | TorchScript over RTNeural |

## Real-time feasibility rules of thumb (from this book's benchmarks — always re-verify on your target)

- Time-domain convolution: real-time up to ~25,000-30,000 coefficients (~0.5-0.6s IR).
- Frequency-domain convolution: ~100-200x faster than time-domain for long IRs.
- TorchScript LSTM: real-time ceiling somewhere around 128-256 hidden units on decent 2020-era hardware — but **actual DAW performance was measurably worse than isolated benchmarks** on some platforms (macOS in the book's tests). Always test in the real host, not just a standalone timing script.
- RTNeural: ~2-3x faster than TorchScript for equivalent architectures; the speed advantage shrinks as the network grows.

## Decision rules

- **"Should I use interactive ML (Wekinator-style) or full supervised training?"** → Interactive (small dataset, live train/infer/train) if the end user should shape the model themselves in real time with a handful of examples. Full supervised training (large dataset, train/val/test split, GPU, many epochs) if you're training the model once, offline, before shipping it to users who only need inference.
- **"Should pitch/duration/velocity be one compound Markov state or separate models?"** → Separate models let patterns recombine creatively but are "not technically perfect" sequence modeling; a compound state is more accurate to the training data but more constrained. The book explicitly leaves this as an experimental choice.
- **"Is my validation loss telling me to stop training?"** → If validation loss is falling alongside training loss, keep going. If validation loss starts rising while training loss keeps falling, stop — you're overfitting.
- **"Do I need `ProcessorDuplicator` for a DSP chain stage?"** → Yes, whenever you add a mono-only processor (like `IIR::Filter`) into a chain alongside stereo-native ones (`WaveShaper`, `Convolution`).
- **"Trace or script a TorchScript export?"** → `trace` for a bare, no-internal-logic model (e.g. raw `torch.nn.LSTM`). `script` for any custom `nn.Module` subclass with its own `forward()` control flow or internal state handling.

## Threshold defaults seen in the book

- Chord detection time threshold: ~50ms (tune per player/instrument).
- IOI/duration modeling bounds: only add values in `[0.05s, 2s]` to avoid modeling excessively long pauses.
- Note-off default duration (before duration modeling): 1 second.
- Markov `needChoices=true`: restrict generation to states with ≥2 possible next observations, to avoid repetitive loops.
- Train/validation/test split: 80/10/10 (`myk_data.get_train_valid_test_datasets` default).
- LSTM training sequence length: 0.5s is a reasonable starting point.
- Warm-up window before computing training loss: ~1000 samples, discarded.
- Truncated BPTT interval: e.g. every 2046 samples (state retained across updates).
- Adam optimizer + `ReduceLROnPlateau(factor=0.5, patience=5)`: halve learning rate after 5 epochs without validation-loss improvement.

## Tells & smells

- **Audible discontinuities every "block length" during LSTM plugin playback** → LSTM state isn't being carried across `processBlock` calls; re-trace the model to accept/return state, or use a model class with internal state handling.
- **Plugin parameters mysteriously off-by-N when reading/writing a hosted plugin** → forgot to apply the same `MIDI CC` parameter filter consistently across print/count/get/set functions.
- **A guitar-amp-style neural model that "sounds right" on its test signal but garbage on anything else** → check validation loss — likely overfit to the training signal, not generalizing.
- **Convolution output sounds clipped/distorted at the DAC** → forgot to normalize by the sum of the impulse-response coefficients.
- **A `unique_ptr`-owned processor suddenly "unusable" after a function call** → it was moved via `std::move`; the original variable no longer owns it.
- **libtorch program crashes silently at `torch::jit::load` on Windows** → Debug/Release build mismatch between your project and the libtorch binary.
- **PyTorch's Linear/Softmax output for an interactive control mapping "fights itself" or stays oddly centered** → softmax forces outputs to sum to 1; wrong for independent parameter outputs — use Linear→Sigmoid→Linear instead (the learner.js/Wekinator architecture).
