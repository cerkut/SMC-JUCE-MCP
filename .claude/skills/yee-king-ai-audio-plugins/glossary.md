# Glossary

**AudioParameterFloat** — a plugin parameter exposed to the host (automation, presets, generic UI); distinct from a plain member variable, which the host can't see (Ch 9, 19, 30).

**AudioProcessorGraph** — JUCE's graph structure for wiring I/O and plugin nodes together with explicit channel/MIDI connections; underlies `AudioPluginHost` (Ch 17).

**Backpropagation ("backprop")** — the algorithm that computes how to adjust network parameters to reduce loss, by propagating error gradients backward through the network (Ch 11, 31).

**Batch** — a subset of a training dataset processed together before one parameter update; an epoch = one full pass over all batches (Ch 31, 34).

**ChordDetector** — the book's class for grouping near-simultaneous MIDI note-ons into a chord using a time threshold, since human-played chords never land at exactly the same sample (Ch 25).

**Compound state** — a Markov state combining multiple event types (e.g. pitch+duration) instead of modeling them as separate chains; contrasted with the book's chosen independent-models approach (Ch 24).

**Convolution** — applying an impulse response to a signal to compute a system's output; can be done in the time domain (simple, slow for long IRs) or frequency domain (FFT-based, much faster) (Ch 27-28).

**DC offset** — a constant shift in a signal's baseline, common in untrained/randomly-initialized LSTM output; penalized by a dedicated loss term during amp-model training (Ch 32, 35).

**DSP Trinity** — the author's named grouping of FIR filters, IIR filters, and waveshapers as the three foundational classical DSP building blocks (Ch 27-30).

**Epoch** — one full pass of the training dataset through the network (Ch 31, 34).

**ESR (Error-to-Signal Ratio) loss** — squared error between output and target, normalized by target signal energy; the primary loss term for amp-model training, from Alec Wright's research (Ch 35).

**FIR (Finite Impulse Response) filter** — output = weighted sum of current + past N *inputs* only (no feedback); analogous to a CNN (Ch 27).

**Frequency response** — how a filter affects different frequencies; the starting point for IIR filter design, since IIR coefficients (unlike FIR) can't be derived directly from a captured impulse response (Ch 29).

**Generalization** — a trained model's ability to perform well on data it has never seen, measured via validation loss (Ch 31, 35).

**Grey-box model** — several black-box modules chained together, informed by a system's high-level structure (e.g. this book's DSP amp chain: pre-amp/tone/cabinet) (Ch 31).

**IIR (Infinite Impulse Response) filter** — output = weighted sum of inputs (feedforward) + weighted sum of the filter's *own past outputs* (feedback); can theoretically ring forever; analogous to an RNN (Ch 29).

**Impulse response** — a system's output when given an impulse (single max-amplitude sample + silence); equals the system's own FIR coefficients for LTI systems (Ch 27).

**Inference** — running a *trained* model to produce output, without computing loss or updating parameters (Ch 31-32).

**Inter-onset-interval (IOI)** — the time gap between consecutive note-ons; modeled as its own Markov chain in the Improviser (Ch 23).

**Interactive machine learning** — Wekinator-style workflow: user provides input-output examples live, trains in real time, tests, adds more examples as needed — small datasets, fast iteration, not statistically rigorous (Ch 12, 15).

**IValue** — TorchScript's generic wrapper type for passing tensors (or tuples of tensors, e.g. LSTM state) into/out of an imported model in C++ (Ch 32-33, 37).

**LTI (Linear Time-Invariant)** — a system property required for the impulse-response/convolution shortcut to work: linear (scaling in → scaling out) + time-invariant (delay in → only delay out). A valve amp is explicitly non-linear, which is why neural modeling is used instead (Ch 27).

**Learning rate** — how far the optimizer adjusts parameters per step along the loss gradient; too high causes oscillation, too low causes slow convergence (Ch 36).

**Learner.js** — Louis McCallum's JavaScript/TensorFlow.js reimplementation of Wekinator; its Linear→Sigmoid→Linear architecture is ported into libtorch for the torchknob (Ch 12, 15).

**Markov model (variable-order)** — a sequence model tracking observation probabilities per state at multiple orders simultaneously, falling back to lower orders when higher-order data is sparse or repetitive (Ch 20-21).

**Meta-controller** — the book's Wekinator-inspired, libtorch-based system for mapping one or more controls to many synth/plugin parameters via a trained neural net (Ch 12-19).

**MarkovManager** — the author's C++ class (`MarkovModelCPP` library) implementing variable-order Markov modeling via `putEvent`/`getEvent` (Ch 21).

**Node (AudioProcessorGraph::Node)** — a wrapper around an `AudioPluginInstance` or I/O processor inside an `AudioProcessorGraph` (Ch 17).

**Overfitting** — when training loss keeps falling but validation loss rises — the model has memorized training data at the cost of generalizing (Ch 31, 35).

**Projucer** — JUCE's original project-generation GUI tool; superseded by CMake in this book once libtorch/RTNeural integration is needed (Ch 3-4).

**RTNeural** — Jatin Chowdhury's header-only, compile-time-templated, inference-only C++ neural network library; 2-3x faster than TorchScript for real-time audio, but training must still happen in PyTorch (Ch 38).

**Sequence length / fragment length** — the chunk size (e.g. 0.5s) that a long training recording is split into for LSTM training; longer = more temporal context, more compute (Ch 35).

**State transition matrix** — the table of probabilities that a given Markov state is followed by each possible observation (Ch 20).

**Tensor** — libtorch's core data structure: scalar → vector → matrix → N-dimensional tensor; everything passed into a neural network must be a tensor (Ch 11, 32).

**TorchScript** — the interchange format (`.pt`/`.ts` files) bridging Python-trained PyTorch models and C++/libtorch inference; exported via `torch.jit.trace` (fixed execution path) or `torch.jit.script` (analyzes actual code, needed for models with internal control flow) (Ch 32-33, 37).

**Truncated Backpropagation Through Time (TBPTT)** — updating LSTM parameters at fixed intervals (e.g. every 2046 samples) while retaining state across those updates, instead of backpropagating across an entire long sequence at once (Ch 36).

**unique_ptr** — a C++ smart pointer with single ownership; `std::move` transfers that ownership (e.g. handing a processor to an `AudioProcessorGraph` node) (Ch 17).

**Validation data** — held-out data (never back-propagated) used during training to detect overfitting; distinct from test data, which compares across different completed training runs (Ch 31, 35).

**Wekinator** — Rebecca Fiebrink's original interactive-ML system (Java/Weka, OSC-based); the direct conceptual ancestor of the meta-controller (Ch 12).

**White-box model** — models a system's actual low-level physical/circuit behavior (e.g. Wave Digital Modelling); accurate but requires deep domain expertise (Ch 31).
