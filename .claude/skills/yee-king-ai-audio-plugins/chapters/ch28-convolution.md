# Chapter 28: Convolution

## Core Idea
Implements time-domain convolution from scratch (WAV in/out via `tinywav`), measures its real-time-feasible limit (~25-27k coefficients), then shows frequency-domain convolution is ~168x faster, before finally using JUCE's own `dsp::Convolution` for a production-quality reverb plugin.

## Key Concepts
- **`tinywav` (Martin Roth's library)**: `myk_tiny::loadWav(path)` returns audio as `vector<float>` in [-1, 1] (converts from whatever the file's sample format is); `myk_tiny::saveWav(buffer, channels, sampleRate, filename)` writes as 16-bit int (`TW_INT16`).
- **Time-domain convolution cost**: real-time feasible up to ~25,000-27,000 coefficients (~0.5-0.6s impulse response) on period hardware — a real cave/hall reverb impulse response is often *longer* than that, motivating frequency-domain convolution.
- **Frequency-domain convolution**: convert signal + impulse response to frequency domain (FFT), multiply (cheap), inverse-FFT back — turns O(n·m) time-domain convolution into an FFT-bounded operation. Constraints: both vectors must be the same length (zero-pad the shorter) and a power of two (truncate the longer to the nearest power of two below its length). Measured ~168x faster than time-domain for a 65,536-sample impulse response.
- **Clipping after convolution**: summing scaled samples can exceed [-1, 1]; **divide the output by the sum of the coefficients** (the theoretical max output value) to prevent clipping.
- **`juce::dsp::ProcessorChain<juce::dsp::Convolution>`**: JUCE's production convolution API — `loadImpulseResponse(file, Stereo::yes, Trim::no, 0)`, then `prepare({sampleRate, blockSize, channels})` in `prepareToPlay`, and `process(ProcessContextReplacing<float>(audioBlock))` in `processBlock`.

## Code Examples
```cpp
// naive time-domain convolution
std::vector<float> conv(std::vector<float> xs, std::vector<float> bs) {
    std::vector<float> y(xs.size() + bs.size(), 0.0f);
    int b_count = bs.size();
    for (int n = 0; n < xs.size(); ++n) {
        y[n] = 0;
        for (int b = 0; b < n && b < b_count; ++b) y[n] += bs[b] * xs[n - b];
    }
    return y;
}
```
```cpp
// preventing clipping: normalize by the sum of coefficients
float sumCoeffs(std::vector<float>& coeffs) {
    float sum = 0.0; for (float& f : coeffs) sum += f; return sum;
}
std::vector<float> y = conv(x, b);
amp(y, 1 / sumCoeffs(b));   // amp() scales the whole buffer in-place
```
```cpp
// JUCE convolution plugin: setup
juce::dsp::ProcessorChain<juce::dsp::Convolution> processorChain;
// in the constructor:
auto& convolution = processorChain.template get<0>();
convolution.loadImpulseResponse(impFile, juce::dsp::Convolution::Stereo::yes,
                                  juce::dsp::Convolution::Trim::no, 0);
// in prepareToPlay:
const auto channels = jmax(getTotalNumInputChannels(), getTotalNumOutputChannels());
processorChain.prepare({sampleRate, (uint32)samplesPerBlock, (uint32)channels});
reset();
// in processBlock:
auto inoutBlock = dsp::AudioBlock<float>(buffer).getSubsetChannelBlock(0, (size_t)numChannels);
processorChain.process(dsp::ProcessContextReplacing<float>(inoutBlock));
```
- **What it demonstrates**: the full arc from hand-written convolution → measured real-time limits → JUCE's production API, all applying the same underlying operation.

## Reference Tables
| Method | Coefficients tested | Time to convolve 2.8s audio |
|---|---|---|
| Time-domain | 25,000 | ~2.68s (near real-time ceiling) |
| Time-domain | 28,000 | ~2.93s (over real-time) |
| Frequency-domain | 65,536 | ~0.012s (M1: ~0.007s) |

## Anti-patterns
- Not normalizing convolution output — summed weighted samples routinely exceed [-1, 1] and get hard-clipped on save; always divide by the coefficient sum (or otherwise normalize).
- Using time-domain convolution for long (>0.5s) impulse responses in real time — frequency-domain convolution is ~168x faster for large impulse responses and is what production reverb plugins actually use.

## Key Takeaways
1. Time-domain convolution is real-time feasible only up to a few tens of thousands of coefficients — insufficient for realistic reverb tails.
2. Frequency-domain convolution (FFT-based) is the practical solution for long impulse responses; requires same-length, power-of-two-sized signal/IR pairs.
3. Always normalize convolution output by the coefficient sum to avoid clipping.
4. JUCE's `dsp::Convolution` inside a `ProcessorChain` gives you production-grade convolution reverb in ~20 minutes of setup code.

## Connects To
- **Ch 27**: the impulse-response theory this chapter operationalizes into actual code.
- **Ch 38**: neural convolution (Steinmetz method) reframes this exact operation using a learned/neural kernel instead of a captured impulse response.
