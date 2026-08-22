---
title: TorchScript Deprecation and Alternatives
author: Cumhur Erkut
---

# TorchScript: Deprecated, and What Replaces It

## Status

TorchScript — the `torch.jit.script` / `torch.jit.trace` toolchain used to export a
model out of Python (e.g. into a JUCE/libtorch plugin, as in this repo's
`Part4_NeuralFX/036b_lstm-torchscript`) — is now deprecated. PyTorch marked it
deprecated in the 2.9/2.10 release cycle, with `torch.export` named as the
direct successor for the "package a model, run it elsewhere" use case
TorchScript used to serve.

## Why it's going away

- TorchScript's Python-subset compiler (`torch.jit.script`) is brittle around
  control flow, dynamic shapes, and newer Python syntax — it requires
  rewriting model code to a scriptable subset.
- PyTorch 2.x's compiler stack (`torch.compile` / Dynamo / Inductor) solves the
  same "capture a graph" problem more robustly, and the team consolidated
  around it instead of maintaining two separate compiler stacks.
- As of mid-2026, parts of the `torch.export` API are still experimental and
  subject to change — this is an active migration, not a finished one.

## Alternatives

| Option | Use case | Notes |
|---|---|---|
| **`torch.export`** | Capture a model as an AOT (ahead-of-time), ATen-level graph | The direct TorchScript successor. Produces an `ExportedProgram` other tools consume. |
| **AOTInductor** | Compile an exported model to a native `.so` for C++ deployment | Closest match to "TorchScript in a JUCE plugin." **Caveat: the `.so` is device-specific** — no cross-platform single artifact like a `.pt` file. |
| **`torch.compile`** | Fast in-Python JIT compilation | Good for server/Python-side inference, not for embedding in a C++ plugin. |
| **ExecuTorch** | Mobile/edge/embedded deployment (Arm, Apple, Qualcomm) | PyTorch's new edge runtime; always consumes a `torch.export`ed graph. Relevant if this ever targets iOS/AUv3. |
| **ONNX + ONNX Runtime** | Framework-agnostic export, run via a separate C/C++ runtime | Mature, widely supported outside the PyTorch ecosystem — arguably the most portable option for a C++ plugin. `torch.onnx.export(..., dynamo=True)` is the new exporter (PyTorch ≥2.6), replacing the legacy TorchScript-based ONNX exporter. Still maturing: some layers (e.g. `FakeQuantize`) only work with the legacy `dynamo=False` path, and Dynamo export isn't supported on Windows yet. |
| **RTNeural** | Real-time-safe neural inference in C++ audio code | Not a PyTorch tool — a separate lightweight header-only library already used in this repo (`037d`/`037e`) as the real-time-safe alternative to running libtorch/TorchScript directly on the audio thread. |

## Relevance to this project's libtorch/Apple Silicon note

The open TODO in `Yee-King-2024.md` (libtorch on Apple Silicon: CPU-only, no
MPS/GPU support in the C++ API) and the book's two parallel LSTM deployment
paths — **libtorch/TorchScript** (`036g`, `037b`) vs. **RTNeural**
(`037d`, `037e`) — point the same direction:

- If the goal is real-time inference inside a plugin, **RTNeural is already
  the more future-proof path** in this codebase, independent of whether
  TorchScript is deprecated — it avoids the libtorch runtime on the audio
  thread entirely.
- If a libtorch-based path is required, plan for **AOTInductor +
  `torch.export`** rather than `torch.jit.script`, keeping in mind
  device-specific compiled artifacts (no more "compile once, run
  anywhere" `.pt` file).
- If the priority is portability across platforms/runtimes rather than
  staying inside the PyTorch/libtorch ecosystem, **ONNX + ONNX Runtime**
  is worth evaluating instead of AOTInductor — a single `.onnx` file (not
  device-specific like an AOTInductor `.so`) that ONNX Runtime's C++ API
  can load directly, avoiding the libtorch dependency in the plugin
  entirely. Trade-off: export coverage from `torch.onnx.export` is still
  maturing for some ops/layers.

## Sources

- [PyTorch 2.10 Release Blog](https://pytorch.org/blog/pytorch-2-10-release-blog/)
- [What's the difference between torch.export / torchserve / executorch / aotinductor?](https://dev-discuss.pytorch.org/t/whats-the-difference-between-torch-export-torchserve-executorch-aotinductor/1642)
- [`jit.export` analogue for `torch.export` (pytorch/pytorch#167631)](https://github.com/pytorch/pytorch/issues/167631)
- [Eight TorchScript Alternatives for the PyTorch 2.x Era](https://medium.com/@Modexa/eight-torchscript-alternatives-for-the-pytorch-2-x-era-34dcb68f2940)
- [torch.onnx — PyTorch main documentation](https://docs.pytorch.org/docs/main/onnx.html)
- [ONNX export fails with dynamo=True (pytorch/pytorch#168969)](https://github.com/pytorch/pytorch/issues/168969)
