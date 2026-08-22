# Chapter 35: Data shapes, LSTM models and loss functions

## Core Idea
Details the dataset shape (`num_sequences × sequence_length × channels`), the `LSTM → Linear` "mix-down" model architecture needed because an N-hidden-unit LSTM outputs N channels (not 1), and Alec Wright's guitar-amp-modeling loss function (pre-emphasis filter + ESR + DC-offset), re-implemented here in PyTorch.

## Frameworks Introduced
- **Wright's 3-stage loss function** (from Alec Wright's guitar-amp-modeling paper, re-implemented here): (1) pre-emphasis filter — a high-pass pre-filter intended to bias later loss stages toward mid/high frequencies (the author found it unnecessary in practice and disabled it); (2) **Error-to-Signal Ratio (ESR) loss** — normalizes squared error by target signal energy; (3) **DC-offset loss** — separately penalizes any constant shift between output and target mean.
- **`LSTM → Linear` "mix-down" architecture**: an `LSTM(1, hidden_size)` outputs `hidden_size` channels (matching its hidden unit count), not 1 — a following `Linear(hidden_size, 1)` layer "mixes down" to mono, exactly as a mixing console sums multiple channels to one.

## Key Concepts
- **Dataset shape**: `(num_sequences, sequence_length, channels)` — a long concatenated input/output recording is chopped into fixed-length fragments (`frag_len_seconds`, e.g. 0.5s); longer sequences give the LSTM more temporal context per training step but cost more compute.
- **Why sequence length matters for stateful systems**: a waveshaper only needs to see 1 sample to know its output; a valve amp's "stateful," feedback-laden behavior needs a longer sequence so the network can learn how *past* samples affect the current output.
- **`TensorDataset` and NumPy dtype/shape discipline**: NumPy arrays must have a regular (non-ragged) shape and an explicit `dtype` (e.g. `np.float32`) before converting to a `torch.Tensor` — a ragged nested list crashes `np.array()`.
- **80/10/10 train/validation/test split** (`myk_data.get_train_valid_test_datasets`, default `splits=[0.8, 0.1, 0.1]`): training data drives parameter updates; **validation** data is unseen-during-training and monitors generalization live (this is what tells you when to stop, per Ch.31's overfitting discussion); **test** data is used once, at the end, to compare across *different training runs* (different sequence length, batch size, learning rate) — distinct purpose from validation.
- **CUDA device selection**: `torch.cuda.is_available()` picks GPU if present, else falls back to CPU (slower but functional) — CUDA = Nvidia's "Compute Unified Device Architecture."
- **`DataLoader`**: wraps a `TensorDataset` to provide batching and shuffling (`DataLoader(train_ds, batch_size=batch_size, shuffle=True)`).

## Code Examples
```python
# why you need a mix-down layer: LSTM output width = hidden unit count, not 1
lstm = torch.nn.LSTM(1, 4, 1)          # 1 input, 4 hidden units
output, _ = lstm.forward(torch.zeros(1, 1))
print(output.shape)   # torch.Size([1, 4]) -- NOT mono!
```
```python
# the model class: LSTM + Linear mix-down
class SimpleLSTM(torch.nn.Module):
    def __init__(self, hidden_size=32):
        super().__init__()
        self.lstm = torch.nn.LSTM(1, hidden_size, batch_first=True)
        self.dense = torch.nn.Linear(hidden_size, 1)   # mix hidden_size -> 1
    def forward(self, torch_in):
        x, _ = self.lstm(torch_in)
        return self.dense(x)
```
```python
# ESR (Error-to-Signal Ratio) loss
def forward(self, output, target):
    self.epsilon = 0.00001
    loss = torch.pow(torch.add(target, -output), 2)
    loss = torch.mean(loss)
    energy = torch.mean(torch.pow(target, 2)) + self.epsilon
    return torch.div(loss, energy)   # normalize error by target signal energy
```
```python
# DC-offset loss
def forward(self, output, target):
    loss = torch.pow(torch.add(torch.mean(target, 0), -torch.mean(output, 0)), 2)
    loss = torch.mean(loss)
    energy = torch.mean(torch.pow(target, 2)) + self.epsilon
    return torch.div(loss, energy)
```
- **What it demonstrates**: (1) the exact reason a raw LSTM output can't be used directly for mono audio, (2) a from-scratch, faithful re-implementation of a published, effective loss function for this specific task (amp emulation), using only differentiable torch ops so it can run on GPU.

## Anti-patterns
- Using plain Euclidean/MSE loss for amp emulation without normalizing by signal energy — the book explicitly notes this "simplest possible loss" isn't appropriate here; ESR (error normalized by target energy) is the better fit.
- Assuming an LSTM's raw output is ready to use as mono audio — it isn't; a `Linear` mix-down layer is required whenever `hidden_size > 1`.
- Creating a NumPy array from ragged (irregular-shape) nested lists — crashes; ensure consistent inner-list lengths before calling `np.array()`.
- Confusing validation data's purpose (live overfitting check, single run) with test data's purpose (final cross-run comparison, e.g. comparing different sequence lengths).

## Key Takeaways
1. `sequence_length` (fragment length fed per training step) controls how much temporal context the network sees — 0.5s is a reasonable starting point, longer for more "stateful" systems.
2. Dataset shape is always `(num_sequences, sequence_length, channels)`; NumPy requires a regular shape and explicit dtype before tensor conversion.
3. An LSTM's output width equals its hidden unit count, not the input's channel count — always follow with a `Linear` mix-down layer for mono audio.
4. Wright's loss = ESR (error normalized by target energy) + DC-offset penalty; the pre-emphasis filter stage was found unnecessary in this author's re-implementation.
5. Validation data (live, per-run, unseen-during-training) and test data (final, cross-run comparison) serve genuinely different purposes — don't conflate them.

## Connects To
- **Ch 32-33**: the LSTM state/shape mechanics this chapter's dataset preparation feeds into.
- **Ch 36**: the actual training loop that uses this model class and these loss functions together.
- **Ch 38**: `save_for_rtneural`, mentioned here as a `SimpleLSTM` method, is used properly in the RTNeural chapter.
