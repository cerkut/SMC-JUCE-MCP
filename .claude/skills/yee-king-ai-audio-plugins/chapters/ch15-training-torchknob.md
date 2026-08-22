# Chapter 15: Training the torchknob

## Core Idea
Implements the full interactive-ML loop for the torchknob: UI "add example" button → `addTrainingData` (stored as tensors) → `runTraining` (SGD + MSE, with an early-exit on tiny loss delta) — then **replaces the softmax output layer with a Linear→Sigmoid→Linear model matching Louis McCallum's learner.js/Wekinator architecture**, because softmax is the wrong tool for independent parameter outputs.

## Frameworks Introduced
- **The learner.js/Wekinator model architecture**: `Linear(n_in, n_out) → Sigmoid → Linear(n_out, n_out)`, no activation after the final layer. Directly ported from Louis McCallum's `learner.js` (TensorFlow.js) into libtorch — chosen because it's "well tested within the Wekinator systems," not derived from first principles.
- **Early-stopping by loss delta**: instead of a fixed epoch count, track `dLoss = previousLoss - loss` and break once `dLoss < 0.00001` — a lightweight substitute for full train/validation/test splitting when the dataset is too small to split.

## Key Concepts
- **`torch::from_blob(...).clone()`**: builds a tensor directly from a `vector<float>`'s raw memory (`.data()`), then `.clone()` copies it so the tensor owns its own memory (the source vector may be reassigned/freed).
- **`std::unique_ptr<torch::optim::SGD>`**: SGD has no default/nullptr-style constructor, so the optimizer must be created *after* the model's `register_module` calls (once `this->parameters()` is known) — hence a smart pointer instead of a plain member.
- **Assertions as a debugging discipline**: `assert(inputs.size() == n_inputs)` inside `addTrainingData` — fail loudly and immediately on shape mismatches rather than producing a confusing downstream bug.
- **Why NOT to use train/validation/test splitting here**: with only a handful of interactively-collected examples, splitting isn't meaningful — the interactive-ML workflow deliberately trades statistical rigor for usability with tiny datasets (explicitly flagged by the author as a departure from "proper" ML practice).

## Code Examples
```cpp
// gathering one training example from the UI
float in   = (float) superKnobTrain.getValue();
float out1 = (float) modDepthSlider.getValue() / modDepthSlider.getMaximum();
float out2 = (float) modIndexSlider.getValue() / modIndexSlider.getMaximum();
nn.addTrainingData({in}, {out1, out2});
```
```cpp
// the corrected model: Linear -> Sigmoid -> Linear (learner.js/Wekinator architecture)
linear1 = register_module("linear1", torch::nn::Linear(n_inputs, n_outputs));
sig1    = register_module("sig1", torch::nn::Sigmoid());
linear2 = register_module("linear2", torch::nn::Linear(n_outputs, n_outputs));
// forward:
torch::Tensor out = linear1(input);
out = sig1(out);
out = linear2(out);   // no activation after the final layer
```
```cpp
// early-stopping training loop
float loss{0}, pLoss{1000}, dLoss{1000};
for (int i = 0; i < epochs; ++i) {
    optimiser->zero_grad();
    auto loss_result = torch::mse_loss(forward(inputs), outputs);
    loss = loss_result.item<float>();
    loss_result.backward();
    optimiser->step();
    dLoss = pLoss - loss;
    pLoss = loss;
    if (i > 0 && dLoss < 0.00001) break;   // converged
}
```
- **What it demonstrates**: replacing a naive fixed-epoch loop with a convergence check; the specific Linear→Sigmoid→Linear shape that supersedes Ch.14's Linear→Softmax model.

## Anti-patterns
- **Softmax for independent parameter outputs (superseded here)**: Ch.14's softmax output forces all outputs to sum to 1, which is wrong when outputs (mod depth, mod index) are independent controls, not a probability distribution. Fixed by switching to the learner.js Linear→Sigmoid→Linear architecture with no final activation constraint.
- Feeding a network two training examples that map the *same* input to *different* outputs and expecting it to satisfy both — it will simply average toward the midpoint to minimize combined error; this is a property of the loss function, not a bug.
- Treating training-set error as sufficient validation for a production ML pipeline — acceptable ONLY because this is a tiny, interactive, small-dataset workflow; the book explicitly does full train/val/test splitting elsewhere (Ch.34-36).

## Key Takeaways
1. Softmax → replaced by Linear→Sigmoid→Linear once independent (non-probability) outputs are needed — the exact fix matches Wekinator/learner.js's own proven architecture.
2. `torch::from_blob(vec.data(), size).clone()` is the efficient vector→tensor conversion pattern; the `.clone()` is required for the tensor to own independent memory.
3. Loss-delta early stopping (`dLoss < 0.00001`) avoids guessing a fixed epoch count; ~5,000-6,000 epochs was typical for this tiny dataset.
4. Interactive ML with a handful of examples deliberately skips train/val/test splitting — that's a workflow choice for usability, not an oversight.

## Connects To
- **Ch 14**: the softmax-based model this chapter explicitly supersedes.
- **Ch 16-19**: this trained torchknob becomes the neural-net core of the full plugin meta-controller.
- **Ch 34-36**: the "proper" full train/val/test workflow the author contrasts this simplified one against.
