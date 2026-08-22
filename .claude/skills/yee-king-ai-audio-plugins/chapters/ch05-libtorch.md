# Chapter 5: Set up libtorch

## Core Idea
Installs libtorch (PyTorch's C++ API) standalone, verifies it with a minimal tensor program, then wires it into the CMake+JUCE plugin skeleton from Ch.4 — the load-bearing chapter for every later neural-audio example.

## Key Concepts
- **Tensor**: libtorch's core data structure — a matrix generalized to arbitrary dimensions (scalar → vector → matrix → N-D tensor).
- **`CMAKE_PREFIX_PATH`**: tells CMake where the unzipped libtorch folder lives, so `find_package(Torch REQUIRED)` can locate it.
- **cxx11 ABI vs pre-cxx11**: pick the cxx11 ABI build when given the choice on the PyTorch download page.
- **Debug vs. Release libtorch build (Windows)**: mismatching a Debug plugin build against a Release libtorch download (or vice versa) causes silent, confusing crashes.

## ⚠️ Apple Silicon note
At time of writing, **no official native libtorch build exists for Apple Silicon (M1/M2)**. The author's workaround is to build PyTorch from source with `-DUSE_MPS=ON`:
```bash
git clone -b main --recurse-submodule https://github.com/pytorch/pytorch.git
mkdir pytorch-build && cd pytorch-build
cmake -DBUILD_SHARED_LIBS:BOOL=ON -DCMAKE_BUILD_TYPE:STRING=Release \
      -DUSE_MPS=ON -DPYTHON_EXECUTABLE:PATH=`which python3` \
      -DCMAKE_INSTALL_PREFIX:PATH=../pytorch-install ../pytorch
cmake --build . --target install
```
This matches (and is the primary literature source for) this project's own libtorch/Apple-Silicon TODO note — `-DUSE_MPS=ON` is a *build-time* flag on a from-source build, not evidence that a stock libtorch binary gets MPS/GPU support "for free."

## Code Examples
```cpp
// minimal libtorch sanity check
#include <torch/torch.h>
#include <iostream>
int main() {
    torch::Tensor tensor = torch::rand({2, 3});
    std::cout << tensor << std::endl;
    return 0;
}
```
```cmake
# minimal libtorch CMakeLists.txt
cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(minimal-libtorch)
set(CMAKE_PREFIX_PATH "../../src_resources/libtorch/libtorch")
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")
add_executable(minimal-libtorch src/main.cpp)
target_link_libraries(minimal-libtorch "${TORCH_LIBRARIES}")
set_property(TARGET minimal-libtorch PROPERTY CXX_STANDARD 17)
```
```cmake
# adding libtorch to an existing JUCE plugin's CMakeLists.txt
set(CMAKE_PREFIX_PATH "../../src_resources/libtorch/libtorch")
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")
# ... then add "${TORCH_LIBRARIES}" to target_link_libraries(...)
```
- **What it demonstrates**: the exact 3-step pattern (prefix path → find_package → link) reused every time libtorch is added to a new project.

## Anti-patterns
- Downloading a Release libtorch on Windows while building your plugin in Debug mode (or vice versa) — crashes silently.
- Typing a from-memory CMakeLists.txt for libtorch integration instead of checking repo-guide 39.2.10 — the exact flags "are subject to change."
- Assuming a stock libtorch download gives you Apple Silicon GPU acceleration — it doesn't; only a from-source `-DUSE_MPS=ON` build even attempts it, and MPS support in libtorch's C++ API remains limited/experimental.

## Key Takeaways
1. `find_package(Torch REQUIRED)` + `CMAKE_PREFIX_PATH` is the whole libtorch-in-CMake pattern; repeated verbatim in every later plugin chapter.
2. Apple Silicon needs a from-source libtorch build; there's no ready-made binary distribution.
3. Windows requires an extra post-build step to copy libtorch's DLLs next to the built executable.
4. The plugin CMakeLists.txt from Ch.4 gains libtorch by adding exactly 3 lines above `target_link_libraries` plus `"${TORCH_LIBRARIES}"` inside it — no other structural change.

## Connects To
- **Ch 11**: first real libtorch neural-net (linear regression) building on this setup.
- **Ch 14, 32, 37**: every later libtorch-based plugin repeats this same CMake pattern.
- **Ch 38**: RTNeural is offered later specifically as a lighter-weight alternative to shipping libtorch at all.
