# Chapter 29: Infinite Impulse Response filters

## Core Idea
Introduces IIR filters — feedback (`a` coefficients acting on *past outputs*) combined with feedforward (`b` coefficients acting on inputs) — as the second DSP Trinity member, explicitly analogized to **recurrent neural networks**, contrasting FIR's analogy to **convolutional neural networks**.

## Frameworks Introduced
- **FIR ≈ CNN, IIR ≈ RNN**: cited from Native Instruments engineers (Kuznetsov, Parker, Esqueda) — FIR filters only look at input history (like a convolution's sliding window); IIR filters feed their own past output back in (like an RNN's hidden state), which is *why* an IIR filter's impulse response can be theoretically infinite from a handful of non-zero inputs.

## Key Concepts
- **General IIR difference equation**: `y[n] = Σ b[i]x[n-i] - Σ a[i]y[n-i]` — feedforward (`b` on inputs) plus feedback (`a` on the filter's *own past outputs*).
- **Why "infinite"**: feeding an IIR filter a short burst of input can produce non-zero output for arbitrarily many steps afterward (demonstrated: 6 non-zero inputs still registering measurable output at step 99) — the feedback term never fully dies out (in general).
- **No direct impulse-response-to-coefficients shortcut for IIR** (unlike FIR): filter design for IIR requires starting from a target *frequency response* (e.g. band-pass) and using filter-design families (Chebyshev, Elliptical) to approximate it — each family trades off passband ripple vs. stopband ripple differently.
- **`juce::dsp::IIR::Coefficients<float>::makeLowPass(sampleRate, freq, Q)`**: JUCE's built-in preset-coefficient generator — no manual filter design needed for common filter types.

## Code Examples
```cpp
// one-pole IIR filter: y[n] = a*y[n-1] + b*x[n]
float a = -0.9, b = 0.5;
float x[] = {0.1, -0.1, 0.2, 0.5, 0.25, 0};
float y[100]; y[0] = 0;
for (int n = 1; n < 100; ++n) {
    float xn = (n < 6) ? x[n] : 0;   // zero-pad past the input's real length
    y[n] = a * y[n-1] + b * xn;
}
```
```cpp
// general N-pole IIR filter applied to a whole signal
std::vector<float> as = {0.5, 0.1, 0.2};   // feedback coefficients
std::vector<float> bs = {0.1, -0.7, 0.9};  // feedforward coefficients
std::vector<float> y(x.size(), 0.0f);
for (auto n = as.size(); n < x.size(); ++n) {
    float yn = 0;
    for (auto bn = 0; bn < bs.size(); ++bn) yn += bs[bn] * x[n - bn];
    for (auto an = 0; an < as.size(); ++an) yn -= as[an] * y[n - an];
    y[n] = yn;
}
```
```cpp
// JUCE IIR plugin setup, using a preset coefficient generator
juce::dsp::ProcessorChain<juce::dsp::IIR::Filter<float>> processorChain;
// in prepareToPlay:
processorChain.prepare({sampleRate, (uint32)samplesPerBlock, (uint32)channels});
auto& filter = processorChain.get<0>();
filter.coefficients = juce::dsp::IIR::Coefficients<float>::makeLowPass(sampleRate, 500, 0.1);
reset();
// processBlock is identical in structure to Ch.28's convolution plugin
```
- **What it demonstrates**: the exact same `ProcessorChain` + `prepare`/`reset`/`process` skeleton as convolution (Ch.28), swapping in an `IIR::Filter` instead — reinforcing that JUCE's DSP module has a uniform interface across effect types.

## Anti-patterns
- Trying to derive IIR filter coefficients directly from a captured impulse response (as you would for FIR/convolution, Ch.27-28) — this shortcut does not exist for IIR; proper filter design (or a preset generator like `makeLowPass`) is required instead.
- Changing filter coefficients mid-block from the GUI thread — the book flags storing GUI-updated parameters and applying them only at the *start* of the next `processBlock` call, to avoid discontinuities mid-buffer.

## Key Takeaways
1. IIR = feedforward (inputs) + feedback (past outputs); FIR is feedforward-only — this feedback is what makes IIR "infinite" and gives it the RNN analogy.
2. There's no impulse-response shortcut for IIR coefficient design (unlike FIR/convolution) — proper filter design or JUCE's preset generators (`makeLowPass`, etc.) are needed.
3. The JUCE `ProcessorChain` skeleton for IIR is structurally identical to convolution (Ch.28) — same `prepare`/`reset`/`process` pattern, different processor type.
4. FIR≈CNN / IIR≈RNN is a named analogy from the neural-effects literature that motivates why later chapters use LSTMs (a kind of RNN) for guitar amp emulation.

## Connects To
- **Ch 27-28**: FIR/convolution, the DSP Trinity member IIR is contrasted against.
- **Ch 32+**: LSTM-based neural amp emulation — the RNN analogy here foreshadows why a recurrent architecture (LSTM) is the natural neural-network counterpart to the amp's feedback-laden analog circuitry.
