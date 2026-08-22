# Chapter 1: Introduction to the book

## Core Idea
The book's mission: make AI-enhanced music systems that usually only exist as inaccessible research code into complete, working, MIT/GPL-licensed plugins that integrate with standard music production workflows (VST/AU, MIDI/OSC) rather than one-off Python scripts.

## Frameworks Introduced
- **Moravec's landscape of human competencies**: AI as a rising sea over a mountainous landscape of human skills — used to frame where AI-music currently stands (chess/Go underwater, guitar-pedal circuit modeling and Bach-chorale generation partially submerged, "picking up a cup" still dry).
- **Book structure**: 4 independent parts after a shared setup part — Meta-Controller (Part 2), Improviser (Part 3), Neural FX (Part 4) — designed so a reader can jump to any one after finishing Part 1.

## Key Concepts
- **AI** (working definition): an automated system performing a task normally requiring human intelligence.
- **Machine learning**: a subset of techniques where the program adjusts its own parameters from data to improve at a task.
- **Dual MIT/GPL licensing**: the author's own code is MIT; using it built against JUCE inherits JUCE's dual license (GPL unless you buy a JUCE commercial license).

## Anti-patterns
- **Research-paper-only AI systems**: papers describe results, not the "nuts and bolts" needed to operationalize them — the book's whole premise is to fix this gap with complete, runnable examples.
- **Quirky one-off Python scripts**: acceptable for research, unusable by actual musicians — the book targets standard plugin formats instead.

## Key Takeaways
1. Four independent example tracks (meta-controller / improviser / neural FX) share only the Part 1 setup — pick and choose after that.
2. All book-authored code is MIT-licensed; JUCE's own dual license (GPL vs. commercial) is a separate, additional consideration if you ship closed-source.
3. Staged repo checkpoints exist for every chapter — use them to unstick a broken build rather than only debugging from scratch.
4. Installers/signing/notarization are explicitly out of scope for this book.

## Connects To
- **Ch 39**: the repository guide, referenced throughout for exact staged-checkpoint paths.
- **Ch 2-9 (Part 1)**: the shared setup all three example tracks depend on.
