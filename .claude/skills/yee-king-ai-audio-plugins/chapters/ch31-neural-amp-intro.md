# Chapter 31: Introduction to neural guitar amplifier emulation

## Core Idea
Frames neural networks as black-box models that overcome classical modeling's trade-offs (white-box = accurate but requires circuit expertise; black-box = simple but can't capture high non-linearity; grey-box = manageable but inherits its sub-components' limits), then walks through the 4-stage supervised training loop and the training/validation/overfitting distinction that governs "when is it trained?"

## Frameworks Introduced
- **White-box / grey-box / black-box modeling** (Vanhatalo et al.): white-box = models the actual circuit (e.g. Wave Digital Modelling of current flow — accurate but requires deep circuit knowledge, computationally expensive); black-box = only cares about input→output response, ignoring internal mechanism (e.g. convolution reverb — "what," not "how"); grey-box = chained black-box modules informed by the system's high-level structure (e.g. this book's Ch.30 amp chain: pre-amp/tone/cabinet as separate black-box stages). Neural networks are **black-box models powerful enough to capture the non-linearity that classical black-box techniques can't**.
- **The FIR/IIR/waveshaper ↔ CNN/RNN/activation-function analogy** (from Ch.29, restated and completed here): CNNs ≈ non-linear FIR filters; RNNs (and their descendant, LSTM) ≈ non-linear IIR filters; a neural network's activation function ≈ waveshaping.
- **The 4-stage training loop**: (1) send test input through the real device, capture output; (2) send the same test input through the network; (3) compute error (loss) between network output and real output; (4) back-propagate to update network parameters; repeat from (2).

## Key Concepts
- **Training data for amp modeling**: a short (~1-2 minutes) varied guitar performance is recorded going into the amp (or captured before/after specific stages: line-out for pre-amp+tone, mic for pre-amp+tone+cabinet). Unlike large-dataset deep learning, amp modeling needs surprisingly little data.
- **Epoch, batch**: an epoch = one full pass over the training dataset; datasets are split into batches, with a parameter update after each batch — batch-parallel processing on GPUs was one of the ideas that enabled the deep learning boom.
- **Validation data / generalizing / overfitting**: hold out 10-20% of data, never back-propagate its error — it measures how well the model performs on *unseen* input. If training loss keeps falling but validation loss rises, the model has **overfit** — memorized training data at the cost of generalizing. Stop training when validation loss stops improving (or starts rising).
- **Training vs. inference environment split**: train in Python (where the ML ecosystem lives), but deploy for **inference** in C++ (real-time, no Python runtime dependency, no web service) — this is *the* recurring workflow for every neural chapter that follows.

## Anti-patterns
- Judging a trained model only on how well it performs on its own training/test signal — the real question is whether it **generalizes** to arbitrary, unseen input, which is what validation data measures.
- Continuing training past the point where validation loss starts rising — this is the overfitting signal to stop on, not falling training loss alone.
- Confusing "training" complexity with "inference" complexity — training needs a GPU-friendly, batch-parallel Python environment; inference (this book's actual deployment target) is comparatively lightweight and runs fine in real-time C++.

## Key Takeaways
1. Neural networks are black-box models, but ones expressive enough to capture the strong non-linearity classical black-box DSP (waveshapers, convolution) can't.
2. CNN≈FIR, RNN/LSTM≈IIR, activation function≈waveshaper — the neural-network/DSP correspondence carried through from Ch.29.
3. Training = iterative (test input → compare to real output → backprop) until loss is low on both training AND held-out validation data; validation is what prevents overfitting.
4. This book's entire remaining workflow: train in Python, deploy for inference in C++/JUCE.

## Connects To
- **Ch 29-30**: the FIR/IIR/waveshaper analogy this chapter completes and reframes as CNN/RNN/activation.
- **Ch 32+**: every subsequent LSTM chapter follows this exact 4-stage training loop and train-in-Python/infer-in-C++ split.
