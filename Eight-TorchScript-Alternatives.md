---
title: Eight TorchScript Alternatives (PyTorch 2.x Era)
author: Cumhur Erkut
source: https://medium.com/@Modexa/eight-torchscript-alternatives-for-the-pytorch-2-x-era-34dcb68f2940
---

# Eight TorchScript Alternatives for the PyTorch 2.x Era

Notes on the Modexa article of the same name, covering eight distinct
successor paths to TorchScript, organized from "stay in Python" to
"vendor/hardware-specific export."

## 1. `torch.compile` (Dynamo + AOTAutograd + Inductor)

Captures a model and compiles optimized kernels without rewriting code or
serializing anything. Best for server-side Python inference. Works best on
CPU/NVIDIA-GPU backends; dynamic shapes are better supported than in earlier
PyTorch but not flawless.

## 2. `torch.export`

An ahead-of-time graph exporter producing a portable, Python-free
representation for downstream runtimes to consume — the direct TorchScript
successor for "export once, run elsewhere." May require resolving graph
breaks and specifying constraints for dynamic shapes.

## 3. ExecuTorch

PyTorch's native edge/mobile runtime (phones, wearables, embedded), the
successor to the now-deprecated PyTorch Mobile. Targets Arm, Apple, and
Qualcomm hardware specifically.

## 4. ONNX + ONNX Runtime

A framework-agnostic export format with multiple execution providers across
CPU/GPU/NPU/browser backends — the most vendor-neutral option here. Trade-off:
universal compatibility sometimes needs an intermediate conversion step to
reach hardware-specific optimizations.

## 5. Torch-TensorRT (NVIDIA)

Brings TensorRT optimizations (layer fusion, kernel auto-tuning) directly into
PyTorch. For production inference on NVIDIA hardware under tight performance
budgets. Operator coverage isn't universal; dynamic shapes need per-model
testing.

## 6. IREE (via Torch-MLIR)

A multi-backend compiler/runtime (Vulkan, Metal, CUDA, CPU) built on MLIR, so
one compilation pipeline can target several backends, including mobile GPUs.
Still a maturing toolchain — expect edge cases on some ops.

## 7. OpenVINO (Intel)

Intel's toolkit for direct PyTorch conversion; can also act as a
`torch.compile` backend. Optimizes for Intel CPUs, Arc GPUs, and emerging
NPUs. Gains are most pronounced on Intel hardware specifically.

## 8. Core ML Tools (Apple)

Converts PyTorch models to `.mlmodel` for native iOS/macOS deployment with
Neural Engine acceleration. Some ops still need workarounds; coverage is
improving over time.

## How this maps onto this project

Of the eight, the ones actually relevant to a JUCE/C++ audio plugin are:

- **ExecuTorch** — if this ever targets a mobile/embedded build (see
  `TorchScript-Alternatives.md` for the ExecuTorch note already logged there).
- **ONNX + ONNX Runtime** — the most portable non-libtorch C++ path; already
  covered in `TorchScript-Alternatives.md`.
- **Core ML Tools** — worth a second look specifically *because* this repo's
  own libtorch/Apple-Silicon TODO (`Yee-King-2024.md`) found no GPU/MPS
  support in libtorch's C++ API. Core ML targets Apple's Neural Engine
  directly and is Apple-native, unlike libtorch on Apple Silicon.
- The remaining four (`torch.compile`, Torch-TensorRT, IREE, OpenVINO) are
  server/Python-inference or non-Apple-hardware paths — not directly
  applicable to a macOS/iOS JUCE plugin, but worth knowing if this project
  ever needs a training/server side.

## Source

- [Eight TorchScript Alternatives for the PyTorch 2.x Era](https://medium.com/@Modexa/eight-torchscript-alternatives-for-the-pytorch-2-x-era-34dcb68f2940) — Modexa, Medium
