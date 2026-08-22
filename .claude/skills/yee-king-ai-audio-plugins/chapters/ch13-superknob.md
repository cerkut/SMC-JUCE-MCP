# Chapter 13: Linear interpolating superknob

## Core Idea
Implements a Yamaha-MODX-style "superknob" — one rotary control mapped to two constrained-range sliders (mod index, mod depth) via linear interpolation (`y = mx + b`), before any neural network is involved. This is the pre-ML baseline the Torchknob (Ch.14) replaces.

## Key Concepts
- **`juce::Slider::ThreeValueHorizontal`**: turns a regular slider into a *range* slider (min/max constraint handles plus a current value) — used so the user can bound the superknob's effective range on each target parameter.
- **`juce::Slider::RotaryHorizontalDrag`**: the "knob" interaction style (click-drag horizontally to rotate) for the superknob control itself.
- **Interpolation as `y = mx + b`**: `weight = targetSlider.getMaxValue() - targetSlider.getMinValue()`; `bias = targetSlider.getMinValue()`; `newValue = superKnobValue * weight + bias` — the superknob's 0-1 range is rescaled into each target's user-constrained range.

## Code Examples
```cpp
// mapping the superknob (0-1) into a constrained target range
double high = modIndexSlider.getMaxValue();
double low  = modIndexSlider.getMinValue();
double weight = high - low;   // m
double bias   = low;          // b

double superV = superKnob.getValue();     // x
double newV = (superV * weight) + bias;   // y
modIndexSlider.setValue(newV);
```
- **What it demonstrates**: the exact regression equation from Ch.10 (`y = mx + b`), applied here with hand-picked weight/bias from slider bounds rather than learned via training — the "manual" precursor to what Ch.14's neural net will learn instead.

## Anti-patterns
- None called out explicitly — this is a scaffolding chapter, deliberately simple before ML is introduced.

## Key Takeaways
1. The superknob is linear interpolation, not machine learning — same `y = mx + b` shape as Ch.10's regression, but with hand-computed weight/bias instead of learned ones.
2. Range-slider `getMinValue()`/`getMaxValue()` let the *user* set the effective range the superknob maps into per parameter — this becomes the user-specifiable "training range" concept later.
3. This is a two-parameter, fixed-mapping baseline — Ch.14 replaces the fixed linear map with a trainable neural net so the mapping can become non-linear and example-driven.

## Connects To
- **Ch 9**: reuses the exact FM synthesizer plugin from that chapter as the target instrument.
- **Ch 14**: replaces this hand-coded linear interpolation with a trained neural network ("torchknob").
