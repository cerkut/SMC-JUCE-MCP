# Chapter 2: Setting up your development environment

## Core Idea
Defines the vocabulary for the whole book's toolchain (build tool, IDE, native vs. interpreted, ML model/training/inference, audio library, plugin/host) and gets a bare "Hello, AI-enhanced audio!" C++ program compiling on Windows/macOS/Linux.

## Key Concepts
- **Build tool (CMake)**: one config file generates projects for multiple IDEs; specifies targets, library links, and build actions.
- **Native vs. interpreted program**: native (C++, compiled) is used for plugins/DAW integration and speed; interpreted (Python) is used for ML experimentation, since research code is usually Python-first.
- **Machine learning model / trained model / inference / generative model**: model = structure + learnable parameters (a "black box"); training adjusts parameters; inference runs a trained model without changing it; a generative model produces new content rather than classifying.
- **Dynamic vs. static linking**: static embeds the library in the binary; dynamic keeps it as a separate file (DLL/.so/.dylib) the app must locate at runtime.
- **Plugin / plugin host / DAW**: a DAW is "an IDE for musicians" that hosts plugins; the book also uses a simpler standalone plugin host for testing.
- **GPU role**: heavy matrix-multiply parallelism speeds up *training*; the book explicitly targets CPU-fast *inference* since end users won't have research GPUs.

## Mental Models
- Training is expensive and needs a GPU sometimes; inference must be cheap enough to run on a plain CPU, because the book's audience is musicians, not researchers with GPU rigs — this constraint shapes every later architecture decision (e.g. why RTNeural matters in ch.38).

## Anti-patterns
- Assuming you need a powerful GPU to work through the book — only *training* is compute-heavy, and inference (the plugin's actual runtime behavior) is designed to run on CPU.

## Code Examples
```cpp
#include <iostream>
int main(){ std::cout << "Hello, AI-enhanced audio!" << std::endl; }
```
- **What it demonstrates**: minimal cross-platform sanity check (`g++ main.cpp -o myprogram`) before any JUCE/libtorch complexity is introduced.

## Key Takeaways
1. CMake is the one build config used across Windows/macOS/Linux instead of per-IDE project files.
2. Training needs compute (sometimes GPU); inference is deliberately kept CPU-cheap — this is a running design constraint, not just a chapter aside.
3. Static vs. dynamic linking will matter later when distributing plugins across machines that don't have your dev libraries installed.
4. Get IDE + CMake + "hello world" working *before* touching JUCE or libtorch — isolate toolchain problems from library problems.

## Connects To
- **Ch 3-5**: install JUCE, CMake, and libtorch on top of this base toolchain.
- **Ch 38**: RTNeural exists precisely because CPU-only real-time inference needs to be fast, echoing this chapter's training/inference split.
