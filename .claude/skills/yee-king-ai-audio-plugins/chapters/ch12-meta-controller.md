# Chapter 12: The meta-controller

## Core Idea
Introduces Rebecca Fiebrink's **Wekinator** (and its JS successor **learner.js**) as the direct inspiration and workflow model for the meta-controller: interactive train→infer→train cycles that map arbitrary-dimension input to arbitrary-dimension output, specialized here for controlling native plugin instruments/effects rather than OSC-connected external tools.

## Frameworks Introduced
- **Wekinator's train-infer-train workflow**: user provides input→output example pairs interactively → trains a model in real time → tests by exploring the trained mapping → adds more examples if needed. Explicitly distinguished from regular ML: interactive, small datasets, "good enough for creative control" rather than statistically rigorous.
- **Meta-controller as a specialized Wekinator**: same interactive-ML workflow, but built in C++/libtorch and wired directly into a plugin host instead of OSC — trades Wekinator's generality for deep integration with real plugins/DAWs.

## Key Concepts
- **Input/output as arrays of numbers**: any human input (webcam frame, trackpad x/y, slider positions) is flattened to a numeric vector before reaching the model; output dimensionality is just "however many parameters you want to control."
- **Wekinator lineage**: original Wekinator (Java + Weka, OSC-based, 2009) → learner.js (JavaScript + TensorFlow.js, browser-based, for the MIMIC live-coding environment).

## Anti-patterns
- Expecting Wekinator-style interactive ML to need large, rigorously curated datasets — the whole point is that small, live-collected example sets are sufficient for "meaningfully controllable," not statistically optimal, creative mappings.
- Wekinator's own OSC-based flexibility is also its integration cost: hooking it to a real plugin/DAW requires manual OSC bridging on both ends — exactly what the meta-controller is built to avoid.

## Key Takeaways
1. The meta-controller sacrifices Wekinator's generality (any input/output via OSC) for direct plugin-host integration.
2. Interactive ML ≠ regular ML: small datasets, live iteration, "controllable" as the bar rather than statistical accuracy.
3. Any human input, however complex, is ultimately just a flat vector of numbers by the time it reaches the model.

## Connects To
- **Ch 13-15**: Superknob → Torchknob is the meta-controller's train-infer-train workflow built incrementally in code.
- **Ch 19**: the full meta-controller generalizes this from one fixed synth to any plugin loaded via a host.
