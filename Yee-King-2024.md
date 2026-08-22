---
author: Cumhur Erkut
title: Build AI-enhanced audio plugins with C++
---

Build AI-Enhanced Audio Plugins with C++ explains how to embed
artificial intelligence technology inside tools that can be used by
audio and music professionals, through worked examples using Python, C++
and audio APIs which demonstrate how to combine technologies to produce
professional, AI-enhanced creative tools.

Alongside a freely accessible source code repository created by the
author that accompanies the book for readers to reference, each chapter
is supported by complete example applications and projects, including an
autonomous music improviser, a neural network-based synthesizer
meta-programmer and a neural audio effects processor. Detailed
instructions on how to build each example are also provided, including
source code extracts, diagrams and background theory. This is an
essential guide for software developers and programmers of all levels
looking to integrate AI into their systems, as well as educators and
students of audio programming, machine learning and software
development. Build AI-Enhanced Audio Plugins with C++ explains how to
embed artificial intelligence technology inside tools that can be used
by audio and music professionals, through worked examples using Python,
C++ and audio plug-in APIs which demonstrate how to combine technologies
to produce professional, AI-enhanced creative tools.

# cerkut notes @ PARTS

## 1 Getting started (18)

### <span class="todo TODO">TODO</span> 5: Set up libtorch (61)

Is libtorch avalailable for Apple Slicon and GPU

As of now, libtorch (the PyTorch C++ API) supports Apple Silicon (M1/M2)
CPUs. However, GPU support on Apple Silicon via libtorch is limited
because Apple Silicon GPUs do not have official CUDA support. Instead,
PyTorch utilizes Apple's Metal Performance Shaders (MPS) backend for GPU
acceleration on Apple Silicon, but this is primarily supported in the
Python API.

For libtorch, MPS support is still experimental or unavailable, so GPU
acceleration on Apple Silicon through libtorch is generally not
supported out-of-the-box. You can use CPU on Apple Silicon with
libtorch, but for GPU, Python API with MPS backend is recommended.

Summary:

- libtorch on Apple Silicon: Yes, CPU supported.
- libtorch on Apple Silicon GPU (MPS): Not officially supported or very
  limited.
- Python PyTorch supports MPS GPU acceleration on Apple Silicon.

If you want GPU acceleration on Apple Silicon, use PyTorch Python API
with MPS rather than libtorch.

``` cpp
#include <torch/torch.h>
#include <iostream>
```

### 6: Python setup instructions (70)

```
print("Hello world")
```

```
import numpy as np
print(np.random.rand())
```

You can confirm your directory by adding this:

```
import os
print(os.getcwd())
```

## 2 Meta Controller (97)

### <span class="done DONE">DONE</span> 10: Using regression for synthesizer control (98)

## 3 Improviser

## 4 NeuralFx

## Study guide

### What musical competences are required for AI?
