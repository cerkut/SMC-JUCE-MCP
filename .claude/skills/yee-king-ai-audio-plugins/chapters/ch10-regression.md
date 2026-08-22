# Chapter 10: Using regression for synthesizer control

## Core Idea
Establishes the theory underpinning the meta-controller: linear regression (`y = mx + b`) generalized to one-to-many mapping (many lines, one input), then reframed as a neural network (`y = wx + b`, weight/bias = slope/intercept) so it can later scale to non-linear many-to-many mappings.

## Frameworks Introduced
- **Regression vs. interpolation**: interpolation forces the line through every data point (breaks on noisy data); regression fits the best line without that constraint — regression is the right tool for noisy, real-world control mappings.
- **One-to-many mapping**: one control (x) drives *N* independent lines, each with its own intercept/gradient, each estimating a different synth parameter. Compared explicitly to the Yamaha ModX "Super-knob" and the Access Virus C's mod-matrix (which only lets you set the multiplier, not the intercept — a named limitation the meta-controller improves on).
- **Neuron ≈ linear equation**: a single feed-forward neural network unit computes `y = wx + b` — identical in form to the regression line, with weight = slope, bias = intercept. Learning = iteratively adjusting `w`/`b` until outputs match examples.

## Key Concepts
- **Weight, bias, parameter**: `w` and `b` are called *parameters*; large models (GPT-scale) simply have billions/trillions of them, but the underlying input→output mechanism is identical to this 2-parameter example.
- **Many-to-many mapping** (the actual meta-controller goal, beyond this chapter's one-to-many): arbitrary-dimension control → arbitrary-dimension parameter set, plus *non-linear* mappings — motivates using a neural net instead of hand-solved regression.

## Anti-patterns
- Using plain linear regression/interpolation when the eventual goal is non-linear, many-to-many mapping — it doesn't scale to that case, which is precisely why the book introduces neural networks instead of stopping at classical regression.

## Key Takeaways
1. A single-neuron feed-forward net *is* a linear regression line — same equation, renamed variables (weight=slope, bias=intercept).
2. Multiple independent lines (one per output parameter) is how one-to-many control mapping works before you even need a "real" neural network.
3. Neural networks are chosen here not because the problem needs deep learning, but because the *workflow* (iterative example-driven fitting) scales cleanly to non-linear, many-to-many mappings later.

## Connects To
- **Ch 11**: implements this exact regression concept using libtorch.
- **Ch 12-13**: the Super-knob/meta-controller directly extend this one-to-many mapping idea into a real plugin.
