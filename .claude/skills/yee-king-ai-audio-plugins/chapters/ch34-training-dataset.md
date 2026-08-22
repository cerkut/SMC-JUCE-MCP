# Chapter 34: Training the amp emulator: dataset

## Core Idea
Walks through the author's `train.py` training program (largely adapting Alec Wright's open-source guitar-amp-modeling code to modern PyTorch practice) — its dataset-loading, TensorBoard integration, and checkpoint-saving structure, rather than building it line-by-line.

## Key Concepts
- **Reviewing vs. writing from scratch**: the author explicitly frames this and following chapters as reviewing an *existing* codebase (partly based on Alec Wright's 2019-2020 guitar-amp-modeling work), rather than the from-scratch build style used for earlier C++ chapters — because reproducing established ML training code line-by-line adds less value than understanding its structure.
- **Training program file layout**: `myk_data.py` (dataset prep), `myk_evaluate.py` (testing trained networks), `myk_loss.py` (loss function definitions), `myk_models.py` (model definitions) — a modular split later chapters (35-37) walk through piece by piece.
- **TensorBoard**: `tensorboard --logdir runs` serves a web dashboard (`http://localhost:6006/`) showing training/validation loss curves per run. Each run gets a timestamped subfolder in `runs/` containing:
  - `events.out.tfevents.*` — TensorBoard's own log data
  - `saved_models/*.pth` — PyTorch model checkpoints, named with epoch and loss (e.g. `lstm_size_32_epoch_3_loss_0.6968.pth`)
  - `saved_models/*.wav` — example outputs from the network at checkpoint time
  - `rtneural_model_lstm_32.json` — the model exported in **RTNeural** format (previewing Ch.38's alternative runtime)

## Code Examples
```bash
# install dependencies
pip install torch torchaudio scipy numpy tensorboard soundfile packaging
# pin a specific version if needed
pip install torch==2.1.0
```
```bash
# run training; expect output like:
python train.py
# Loading dataset from folder ../../data/audio_ht1
# generate_dataset:: Loaded frames from audio file 120
# Splitting dataset
# Looking for GPU power
# cuda device not available/not selected
# Creating model / data loaders / optimiser / loss functions
# About to train
# epoch, train, val
# 0 0.7639494 0.7458705
```
```bash
# watch training progress live
tensorboard --logdir runs
```
- **What it demonstrates**: the expected first-run console output (a checklist to confirm the environment is correctly set up before debugging further), and how to monitor an in-progress training run visually.

## Anti-patterns
- Debugging training failures by guessing — the chapter's explicit advice is: read `ModuleNotFound` errors as missing pip installs, and assertion errors as usually a training-data-folder path mismatch (default expects `../../data/audio_ht1` two levels up).
- Skipping TensorBoard monitoring — without it you can't see whether training/validation loss is actually converging or diverging (overfitting, per Ch.31) until training completes.

## Key Takeaways
1. This chapter's `train.py` is adapted from prior open-source work (Alec Wright), not built from first principles — the goal is understanding its structure, not re-deriving it.
2. `.pth` files are point-in-time model checkpoints; the accompanying `.json` is the same model already exported to RTNeural format, and `.wav` files are example outputs — all auto-generated per checkpoint.
3. TensorBoard (`tensorboard --logdir runs`) is the standard way to watch training/validation loss curves live during a run.
4. Common first-run failures are either missing pip packages or a training-data folder path mismatch — check those first.

## Connects To
- **Ch 31**: the training/validation/epoch theory this chapter's `train.py` actually implements.
- **Ch 35-36**: walk through `myk_data.py`/`myk_models.py`/`myk_loss.py` and the training loop internals in detail.
- **Ch 38**: the RTNeural JSON export seen here in the `runs/` folder structure is used properly in that chapter.
