---
name: yee-king-ai-audio-plugins
description: "Knowledge base from \"Build AI-Enhanced Audio Plugins with C++\" by Matthew John Yee-King. Use when applying Yee-King's frameworks for JUCE plugin development, libtorch/RTNeural neural audio effects, interactive machine learning (meta-controller/Wekinator-style), variable-order Markov sequence modeling, or classical DSP (FIR/IIR/waveshaping), studying the book, or referencing its concepts."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Build AI-Enhanced Audio Plugins with C++
**Author**: Matthew John Yee-King | **Pages**: ~340 | **Chapters**: 39 | **Generated**: 2026-08-22

## How to Use This Skill

- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `torchknob`, `Markov improviser`, `RTNeural`, or another indexed topic; I find and read the relevant chapter
- **With chapter** — ask for `ch32`; I load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

**The Meta-Controller** (Ch 12-19): a Wekinator-derived interactive-ML system mapping one control to many plugin parameters. Evolves Superknob (hand-coded linear interpolation) → Torchknob (untrained, then trained, neural net) → full meta-controller (generalizes to *any* hosted plugin via `AudioProcessorGraph` + parameter introspection). Uses the **train-infer-train workflow**: user provides input-output examples live, trains in real time, tests, adds more if needed — small datasets are sufficient because the goal is "controllable," not statistically optimal.

**Variable-order Markov modeling** (Ch 20-25): the Improviser's core technique. Track transition matrices at several orders simultaneously; prefer the highest order with data available; fall back to a lower order when a state has ≤1 observation (avoids repetitive loops). Applied independently to pitch, IOI, duration, velocity, and polyphonic (chord) states. Chosen over neural nets specifically because it trains live, from a single short performance, cheaply.

**The DSP Trinity → neural network correspondence** (Ch 27-31): FIR filter ≈ CNN (feedforward only, no state); IIR filter ≈ RNN (feedback, can theoretically "ring" forever); waveshaper ≈ activation function. A guitar amp's signal chain (pre-amp → tone → power amp → cabinet) is a **grey-box model**: waveshaper + IIR + waveshaper + FIR/convolution. Neural networks are black-box models powerful enough to capture non-linearity that classical black-box techniques (waveshaping, convolution) can't — motivating LSTM-based amp emulation.

**LSTM state must be threaded across audio blocks** (Ch 33, 37): a naive block-based `processBlock` resets the LSTM's internal state every call, causing audible discontinuities at block boundaries. Fix: re-trace/script the model to explicitly accept and return a state tuple (`LSTMState` = `(h0, c0)`), and thread it manually — or use a model class (like `SimpleLSTM`) that manages state internally.

**Train in Python, infer in C++** (Ch 31-38): design/train/export in Python (rapid iteration, GPU access, plotting) → deploy for real-time inference in C++/JUCE. Two export paths: **TorchScript** (`torch.jit.trace` for stateless models, `torch.jit.script` for models with internal control flow; full torch coverage, slower) vs. **RTNeural** (JSON weight export, compile-time C++ templates, 2-3x faster, inference-only, narrower layer support, requires the C++ architecture to exactly match the JSON).

**Training discipline** (Ch 31, 35-36): 4-stage loop (send test input through the real device → send through network → compute loss → backprop, repeat). Validation data (held out, never backpropagated) detects overfitting — if training loss falls but validation loss rises, stop. Truncated Backpropagation Through Time (interval parameter updates with retained state) trains better and cheaper than full-sequence backprop for stateful models. Loss for amp emulation = ESR (error normalized by signal energy) + DC-offset penalty, not plain MSE.

**Wright's ESR + DC-offset loss** (Ch 35): `ESR = mean((target-output)²) / (mean(target²) + ε)`; `DC = mean((mean(target) - mean(output))²) / (mean(target²) + ε)`. Plain Euclidean/MSE loss is explicitly called out as inappropriate for amp emulation — always normalize by signal energy.

**Softmax vs. Sigmoid for independent parameter outputs** (Ch 14-15): softmax forces outputs to sum to 1 — wrong when outputs are independent controls (mod depth, mod index), not a probability distribution. Fixed by adopting the proven Wekinator/learner.js architecture: Linear → Sigmoid → Linear, no final activation.

**Audio-thread safety discipline** (Ch 16, 22): never let UI-thread events (MIDI clicks, slider drags) touch the audio processor directly — buffer them, merge into processor state only inside `processBlock`, on your own schedule. Scheduled note-offs use a per-note `noteOffTimes[127]` array checked each block, not sample-accurate timers.

**JUCE plugin fundamentals** (Ch 3-9, 16-19): CMake (not Projucer) once libtorch/RTNeural integration is needed; `processBlock(AudioBuffer&, MidiBuffer&)` is the one function every synth/effect/host revisits; `AudioParameterFloat` + `addParameter()` exposes host-automatable parameters (plain member variables are invisible to hosts); `AudioProcessorGraph` + explicit node connections generalizes single-plugin hosting to arbitrary chains.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-introduction.md) | Introduction to the book | book structure, licensing |
| [ch02](chapters/ch02-dev-environment.md) | Setting up your development environment | build tool/IDE/ML vocabulary |
| [ch03](chapters/ch03-installing-juce.md) | Installing JUCE | Projucer, Standalone target |
| [ch04](chapters/ch04-cmake.md) | Installing and using CMake | CMake JUCE plugin skeleton |
| [ch05](chapters/ch05-libtorch.md) | Set up libtorch | libtorch install, Apple Silicon note |
| [ch06](chapters/ch06-python-setup.md) | Python setup instructions | Python/C++ division of labor |
| [ch07](chapters/ch07-common-setup-problems.md) | Common dev-environment setup problems | troubleshooting table |
| [ch08](chapters/ch08-basic-plugin.md) | Basic plugin development | processBlock, sine synth |
| [ch09](chapters/ch09-fm-synth.md) | FM synthesizer plugin | AudioParameterFloat |
| [ch10](chapters/ch10-regression.md) | Using regression for synthesizer control | linear regression, weight/bias |
| [ch11](chapters/ch11-libtorch-regression.md) | Experiment with regression and libtorch | libtorch training loop |
| [ch12](chapters/ch12-meta-controller.md) | The meta-controller | Wekinator, train-infer-train |
| [ch13](chapters/ch13-superknob.md) | Linear interpolating superknob | manual interpolation |
| [ch14](chapters/ch14-torchknob.md) | Untrained torchknob | NeuralNetwork wrapper class |
| [ch15](chapters/ch15-training-torchknob.md) | Training the torchknob | softmax→sigmoid fix |
| [ch16](chapters/ch16-plugin-meta-controller.md) | Plugin meta-controller | plugin hosting basics |
| [ch17](chapters/ch17-audioprocessgraph.md) | Placing plugins in an AudioProcessGraph | graph-based hosting |
| [ch18](chapters/ch18-plugin-ui.md) | Show a plugin's user interface | PluginWindow, listener pattern |
| [ch19](chapters/ch19-full-meta-controller.md) | From plugin host to meta-controller | dynamic parameter sizing |
| [ch20](chapters/ch20-sequencers-background.md) | Background: all about sequencers | variable-order Markov theory |
| [ch21](chapters/ch21-markov-models-cpp.md) | Programming with Markov models | MarkovManager API |
| [ch22](chapters/ch22-improviser-plugin.md) | Starting the Improviser plugin | MIDI buffering, note-off scheduling |
| [ch23](chapters/ch23-note-onset-times.md) | Modelling note onset times | IOI modeling |
| [ch24](chapters/ch24-note-duration.md) | Modelling note duration | duration modeling |
| [ch25](chapters/ch25-polyphonic-markov.md) | Polyphonic Markov model | ChordDetector, velocity model |
| [ch26](chapters/ch26-neural-fx-welcome.md) | Welcome to neural effects | effects history, DDSP |
| [ch27](chapters/ch27-fir-signals-systems.md) | Finite Impulse Responses, signals and systems | FIR, impulse response, LTI |
| [ch28](chapters/ch28-convolution.md) | Convolution | time/freq-domain convolution |
| [ch29](chapters/ch29-iir-filters.md) | Infinite Impulse Response filters | IIR, filter design |
| [ch30](chapters/ch30-waveshapers.md) | Waveshapers | nonlinear transfer functions |
| [ch31](chapters/ch31-neural-amp-intro.md) | Introduction to neural guitar amplifier emulation | white/grey/black-box, training theory |
| [ch32](chapters/ch32-lstm-network.md) | Neural FX: LSTM network | TorchScript export/import |
| [ch33](chapters/ch33-juce-lstm-plugin.md) | JUCE LSTM plugin | LSTM state threading |
| [ch34](chapters/ch34-training-dataset.md) | Training the amp emulator: dataset | train.py, TensorBoard |
| [ch35](chapters/ch35-data-shapes-loss.md) | Data shapes, LSTM models and loss functions | ESR/DC loss, dataset shapes |
| [ch36](chapters/ch36-training-loop.md) | The LSTM training loop | TBPTT, warm-up, scheduler |
| [ch37](chapters/ch37-operationalise-plugin.md) | Operationalising the model in a plugin | jit.script deployment |
| [ch38](chapters/ch38-rtneural.md) | Faster LSTM using RTNeural | RTNeural vs TorchScript |
| [ch39](chapters/ch39-repository-guide.md) | Guide to the projects in the repository | repo navigation index |

## Topic Index

- **AudioProcessorGraph / plugin hosting** → ch16, ch17, ch19
- **ChordDetector / polyphony** → ch25
- **CMake (JUCE + libtorch)** → ch04, ch05, ch28-30
- **Convolution (time & frequency domain)** → ch27, ch28
- **DSP Trinity (FIR/IIR/waveshaper)** → ch27, ch29, ch30
- **Interactive machine learning / Wekinator** → ch12, ch15
- **IOI / note duration modeling** → ch23, ch24
- **LSTM (Python)** → ch32, ch35, ch36
- **LSTM (C++/JUCE deployment)** → ch33, ch37, ch38
- **Markov models (variable-order)** → ch20, ch21
- **Meta-controller** → ch10-ch19
- **MIDI processing / note-off scheduling** → ch22, ch23
- **Overfitting / validation** → ch31, ch35
- **RTNeural** → ch38
- **TorchScript** → ch32, ch33, ch37
- **Training loop / loss functions** → ch11, ch31, ch34-ch36
- **Waveshaping / amp chain** → ch30, ch31

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the book content only. For hands-on implementation in your codebase, combine with project-specific tools — e.g. this project's `graphify-out/graph.json` knowledge graph of the book's companion GitHub repository ([yeeking/ai-enhanced-audio-book](https://github.com/yeeking/ai-enhanced-audio-book)), which cross-links directly to concepts in this skill (e.g. `036b_lstm-torchscript`, `037e_lstm-rtneural-JUCE`). For topics beyond this book, check related skills or ask the agent directly.
