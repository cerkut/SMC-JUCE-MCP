# Chapter 6: Python setup instructions

## Core Idea
Sets up Python purely as a training/analysis tool — the book's actual applications are C++; Python is used only where PyTorch's Python-first ecosystem makes training and dataset work dramatically easier than doing it in C++.

## Key Concepts
- **Division of labor**: Python = training neural nets + some analysis; C++ = the shipped application/plugin. Not all book examples need Python — only the neural-network training chapters do.
- **Virtual environments**: recommended over a bare global Python install to avoid dependency conflicts between projects.
- Python version pinned/tested up to **3.10** for this book's code.

## Anti-patterns
- Expecting deep Python-code walkthroughs at the same level of detail as the C++ chapters — the author deliberately explains Python code more lightly, since "machine learning in Python is very well covered in other books."

## Key Takeaways
1. Only some book examples need Python at all — most of the book is pure C++.
2. Use a virtual environment per project rather than a single global Python install.
3. Python 3.10 is the tested baseline; newer versions may or may not work with pinned dependency versions.

## Connects To
- **Ch 34-36**: the Python LSTM training scripts assume this Python setup is already working.
- **Ch 11, 14-15**: the meta-controller's libtorch-in-C++ path is an alternative to doing everything in Python.
