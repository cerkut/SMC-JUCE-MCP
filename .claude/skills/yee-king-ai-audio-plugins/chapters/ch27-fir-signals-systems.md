# Chapter 27: Finite Impulse Responses, signals and systems

## Core Idea
Introduces the "DSP Trinity" (FIR, IIR, waveshapers) starting with FIR filters as weighted sums of past inputs, and the crucial **impulse response = coefficients** relationship that convolution (Ch.28) depends on — gated by the **linear time-invariant (LTI)** property that explains later *why* modeling a valve guitar amp is hard.

## Frameworks Introduced
- **The "DSP Trinity"**: FIR filters, IIR filters, waveshapers — the author's named grouping of the three foundational DSP building blocks, each later connected to a neural-network analogue (FIR≈convolution layer, IIR≈recurrent/stateful layer, waveshaper≈nonlinear activation).
- **General FIR form**: `y[n] = Σ(i=0..N) b[i] * x[n-i]` — output is a weighted sum of the current and past N inputs, weights = coefficients `b`.

## Key Concepts
- **Impulse response = coefficients**: for an LTI system, sending in an impulse (a single max-amplitude sample followed by silence) produces an output *equal to the system's own filter coefficients*. This is why you can capture a real space or effect's "sound" by recording its response to a click, then reuse that recording as filter coefficients on any other signal (this is convolution, Ch.28).
- **Linear**: doubling the input doubles the output (holds for scalars generally); **additivity**: passing two signals separately and summing outputs = passing their sum in once. A valve guitar amp is explicitly non-linear (gain changes tone, not just loudness) — that's *why* it's hard to convolution-model and *why* neural nets are used instead.
- **Time-invariant**: a delayed input produces only a delayed (not otherwise changed) output — the system's behavior doesn't change over time. A parameterized effect (e.g. reverb room size) is still LTI *for a fixed parameter setting* — changing the parameter just switches to a different LTI system.

## Code Examples
```cpp
// one-pole filter (volume control): y[n] = b * x[n]
float b = 0.5;
float x[] = {0.1, -0.1, 0.2};
float y[3];
for (int n = 0; n < 3; ++n) y[n] = b * x[n];
```
```cpp
// two-pole averaging filter (crude low-pass): y[n] = b0*x[n] + b1*x[n-1]
float b0 = 0.5, b1 = 0.5;
float x[] = {0.1, -0.1, 0.2};
float y[3];
for (int n = 1; n < 3; ++n) y[n] = b0*x[n] + b1*x[n-1];
```
```cpp
// general N-coefficient FIR filter applied to a whole signal
int N = 3, sig_len = 6;
float b[] = {0.25, 0.5, 0.25};
float x[] = {0.1, -0.1, 0.2, 0.5, 0.25, 0.1};
float y[] = {0, 0, 0, 0, 0, 0};
for (int n = N; n < sig_len; ++n)
    for (int i = 0; i < N; ++i)
        y[n] += b[i] * x[n - i];
```
- **What it demonstrates**: FIR filtering is a weighted sum of a signal's recent history — the "1-pole → 2-pole → N-pole" progression is literally "how many past samples does this filter look at."

## Anti-patterns
- Assuming impulse-response capture-and-reuse (convolution) works for *any* effect — it only works for LTI systems; a valve amp's non-linearity is precisely why this technique fails there and neural modeling is needed instead.

## Key Takeaways
1. FIR filter = weighted sum of current + past N samples; more poles = longer memory = more complex frequency shaping.
2. Impulse response IS the coefficient set for an LTI system — capture a room/effect's impulse response once, apply it to any signal forever after (convolution).
3. LTI = linear (scaling in → scaling out, additivity holds) + time-invariant (delay in → only delay out, behavior doesn't change over time).
4. Non-linearity (like a valve amp's gain-dependent distortion) is exactly what breaks the convolution shortcut — motivating the neural-network approach in later chapters.

## Connects To
- **Ch 28**: convolution — the practical technique this chapter's impulse-response theory enables.
- **Ch 29**: IIR filters, the second DSP Trinity member (adds feedback/state, unlike FIR).
- **Ch 30-32**: waveshapers and neural nets specifically because they *aren't* constrained to LTI systems, unlike FIR/IIR.
