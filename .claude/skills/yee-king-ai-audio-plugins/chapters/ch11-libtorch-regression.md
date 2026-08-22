# Chapter 11: Experiment with regression and libtorch

## Core Idea
The canonical libtorch training-loop pattern: generate noisy synthetic data → build a `torch::nn::Linear` model → convert to tensors → compute MSE loss → SGD optimizer step, repeated until loss drops below a threshold. This exact loop shape recurs in every later training chapter.

## Frameworks Introduced
- **The libtorch training loop** (canonical form, reused throughout the book):
  ```
  out = net(input)
  loss = mse_loss(out, target)
  optimizer.zero_grad()
  loss.backward()
  optimizer.step()
  ```
  Repeat until loss is acceptably low. "Epoch" = one pass over the whole dataset; for large datasets this is batched, but the book's tiny regression dataset fits in a single batch.

## Key Concepts
- **`torch::nn::Linear(in, out)`**: `y = xAᵀ + b` — same shape as `y = mx + b`; `Linear(1,1)` has 2 parameters (weight, bias), `Linear(2,3)` has 6 weights + 3 biases (fully connected).
- **Tensor construction**: `torch::empty({rows, cols})` allocates, then index like an array (`t[i][0] = value`) to fill it — floats must always be wrapped in tensors before reaching the network.
- **Batched inference**: passing the *entire* input dataset as one tensor to `net(in_t)` computes all outputs in one call — no manual looping over rows needed.
- **`torch::mse_loss(output, target)`**: mean squared error between network output and ground truth.
- **`torch::optim::SGD(net->parameters(), lr=0.01)`**: stochastic gradient descent optimizer; `lr` is the learning rate.
- **Debug/Release build parity**: on Windows, the libtorch build mode (Debug/Release) must match your project's build mode.

## Code Examples
```cpp
// dataset generation: noisy line
std::vector<std::pair<float,float>> getLine(float b, float m, float startX, float endX, float count) {
    float y{0}, dX{0};
    std::vector<std::pair<float,float>> xys;
    dX = (endX - startX) / count;
    for (float x = startX; x < endX; x += dX) {
        y = (m * x) + b;
        xys.push_back({x, y});
    }
    return xys;
}

void addNoiseToYValues(std::vector<std::pair<float,float>>& xys, float low, float high) {
    std::default_random_engine generator;
    std::uniform_real_distribution<float> distribution(low, high);
    auto rand = std::bind(distribution, generator);
    for (int i = 0; i < xys.size(); ++i) xys[i].second += rand();
}
```
```cpp
// model, tensors, training loop
auto net = torch::nn::Linear(1, 1);

torch::Tensor in_t = torch::empty({(long)xys.size(), 1});
for (int i = 0; i < xys.size(); ++i) in_t[i][0] = xys[i].first;

torch::Tensor correct_t = torch::empty({(long)xys.size(), 1});
for (int i = 0; i < xys.size(); ++i) correct_t[i][0] = xys[i].second;

torch::optim::SGD optimizer(net->parameters(), /*lr=*/0.01);

float loss = 1000;
while (loss > 0.5) {
    torch::Tensor loss_t = torch::mse_loss(net(in_t), correct_t);
    loss = loss_t.item<float>();
    optimizer.zero_grad();
    loss_t.backward();
    optimizer.step();
}
```
- **What it demonstrates**: the complete, minimal libtorch train-a-model pattern — every neural chapter after this one (torchknob, LSTM) is a variation on this same 5-line loop.

## Reference Tables
| Step | libtorch call |
|---|---|
| Build model | `torch::nn::Linear(in, out)` |
| Forward pass | `net(input_tensor)` |
| Compute loss | `torch::mse_loss(output, target)` |
| Reset gradients | `optimizer.zero_grad()` |
| Backprop | `loss.backward()` |
| Apply update | `optimizer.step()` |

## Anti-patterns
- Passing raw `float`s directly into a libtorch network — everything must be wrapped in a `torch::Tensor` first.
- Expecting zero loss — a perfect fit through noisy data is impossible; the loop should target a "good enough" threshold, not zero.
- Recreating a random number generator on every call — inefficient (acknowledged directly in the text as a simplification, not a recommended pattern for production code).

## Key Takeaways
1. This 5-step loop (forward → loss → zero_grad → backward → step) is THE libtorch training pattern reused throughout the book.
2. A `Linear(1,1)` layer is mathematically identical to 1D linear regression; parameter count scales as `inputs × outputs` weights plus `outputs` biases.
3. Pass entire datasets as one tensor for batched inference — no manual per-row looping needed at inference time.
4. SGD's learning rate (`lr`) and the noise level in the dataset both affect how many epochs training needs.

## Connects To
- **Ch 14-15**: the torchknob's neural net training loop is a direct extension of this one.
- **Ch 34-36**: the LSTM training pipeline follows the same forward→loss→backward→step shape, just with a more complex model and dataset.
