# Chapter 36: The LSTM training loop

## Core Idea
Details `train_epoch_interval` — the training loop's three special techniques (warm-up, state-zeroing between batches, and truncated backpropagation through time) that make LSTM amp-model training actually work well, plus the Adam optimizer + `ReduceLROnPlateau` scheduler combination controlling how parameters get updated.

## Frameworks Introduced
- **Truncated Backpropagation Through Time (TBPTT)**: instead of running backprop across an entire long sequence, update parameters every N samples (e.g. every 2046) while *retaining* LSTM state across those updates. Cited from Wright's research as producing better training results than long, infrequent updates — trades some computational complexity for more frequent, cheaper parameter updates.
- **Warm-up steps**: pass the first ~1000 samples of a sequence through the network and *discard* their loss before starting real loss accumulation — avoids training being distorted by the same "state hasn't filled up yet" dip observed in Ch.33's block-processing artifacts.

## Key Concepts
- **Optimizer + scheduler pairing**: `torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)` updates parameters along the loss gradient; `torch.optim.lr_scheduler.ReduceLROnPlateau(optimiser, 'min', factor=0.5, patience=5)` automatically halves the learning rate when validation loss plateaus — prevents the "oscillating, never settling" symptom of a learning rate that's too high for the current stage of training.
- **`zero_on_next_forward`**: explicitly resets LSTM state to zero between batches (a model method from Ch.35's `SimpleLSTM`), ensuring each new batch starts from a known, clean state rather than carrying over unrelated prior-batch context.
- **Model checkpoint/exit logic**: after each epoch, save weights only if validation loss is a new record; exit early if no new record for a patience window, or if `max_epochs` is reached — a lightweight automated version of the manual "watch the validation curve" process from Ch.31.
- **Learning rate intuition**: too high → loss oscillates and never settles (overshoots the gradient-indicated adjustment each step); too low → training crawls. The scheduler exists specifically to reduce the rate once oscillation/plateau is detected.

## Code Examples
```python
# per-run logging/checkpoint folder, tied to TensorBoard's own log dir
writer = SummaryWriter(comment='32 node LSTM amp')
model_save_dir = writer.get_logdir() + "/saved_models/"
os.makedirs(os.path.dirname(model_save_dir), exist_ok=True)
```
```python
# optimizer + adaptive learning-rate scheduler
optimiser = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimiser, 'min', factor=0.5, patience=5, verbose=True)
```
- **What it demonstrates**: the standard PyTorch optimizer/scheduler setup pattern used for the rest of the book's training work.

## Reference Tables
| Feature | Purpose |
|---|---|
| Warm-up (~1000 samples, discarded) | avoid loss contamination from the LSTM's "not yet filled up" state dip |
| `zero_on_next_forward` between batches | guarantee clean state per batch, no cross-batch memory bleed |
| Truncated BPTT (interval updates, e.g. every 2046 samples) | more frequent, cheaper parameter updates than full-sequence backprop; state retained across intervals |
| `ReduceLROnPlateau` scheduler | halve learning rate when validation loss plateaus, stabilizing convergence |
| Checkpoint-on-new-record + patience-based early exit | automated stop-before-overfitting per Ch.31/35 |

## Anti-patterns
- Backpropagating across an entire long training sequence in one step — expensive and, per Wright's findings, trains *worse* than truncated (interval-based) backprop.
- Skipping the warm-up discard — the LSTM's early-in-sequence "state not yet filled" behavior would otherwise be treated as real error signal and distort training.
- Leaving the learning rate fixed throughout training — without a scheduler, a rate tuned for early training tends to cause oscillation once the network is close to converged.

## Key Takeaways
1. TBPTT (interval-based backprop with retained state) is the key technique making LSTM amp-model training practical — full-sequence backprop is both slower and, per the cited research, worse.
2. Warm-up steps discard early-sequence loss to avoid the LSTM's fill-up transient contaminating training.
3. Adam + `ReduceLROnPlateau` is the standard optimizer/scheduler pairing used here — the scheduler exists to counteract a fixed learning rate's tendency to oscillate near convergence.
4. Checkpointing on new validation-loss records, combined with a patience-based early exit, automates the "stop before overfitting" discipline from Ch.31/35.

## Connects To
- **Ch 33**: the LSTM state-reset artifact this chapter's warm-up step specifically works around.
- **Ch 34-35**: the dataset/model/loss components this training loop actually drives.
- **Ch 37**: takes the checkpoints (`.pth` files) this loop produces and deploys them into the plugin from Ch.33.
