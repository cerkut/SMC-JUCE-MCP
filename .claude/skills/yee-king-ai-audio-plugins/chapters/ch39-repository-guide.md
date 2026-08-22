# Chapter 39: Guide to the projects in the repository

## Core Idea
A navigational index into the book's companion GitHub repository — every "repo-guide section X.Y.Z" reference scattered through Chapters 1-38 points here. Organizes projects by book part, and separately lists the 3 "complete," most-polished final versions of each major example plus supporting test tools.

## Key Concepts
- **Complete projects** (the finished, most-polished version of each major example):
  - **Meta-controller**: `Part2_MetaController/010e_metacontroller`
  - **Improviser**: `Part3_Improviser/020h_midi_markov_vel`
  - **Neural FX**: `Part4_NeuralFX/037e_lstm-rtneural-JUCE`
- **Test tools** (in `TestTools/`): `AudioPluginHost`, `MykScope` (oscilloscope), and other diagnostic/utility plugins used throughout the book's testing workflow.
- **Numbering convention**: each chapter's incremental build stages are numbered projects (e.g. `003a/b/c_sineplugin*`, `037a-037e_lstm-*`) — matching the repo-guide section numbers cited inline throughout Chapters 1-38 (e.g. "repo guide section 39.2.10" = the minimal libtorch project).
- **Repository structure mirrors book Parts**: `Part1_GettingStarted`, `Part2_MetaController`, `Part3_Improviser`, `Part4_NeuralFX`, plus `TestTools` and (per Ch.32-38) an `RTNeural` submodule and Python training scripts.

## Key Takeaways
1. This chapter is a lookup table, not a tutorial — its value is jumping directly to a working checkpoint when stuck on a chapter's exercises, rather than typing every listing by hand.
2. Each Part's three "complete" projects represent the fully-built end-state of that Part's example — useful starting points for experimentation once you've worked through the tutorial chapters once.
3. The numbering scheme (`NNNx_description`) lets you locate the exact project referenced by any "repo-guide section X.Y.Z" citation elsewhere in the book.

## Connects To
- **Every prior chapter (1-38)**: this is the index those "repo guide section 39.X.Y" citations resolve to.
- The companion GitHub repository [yeeking/ai-enhanced-audio-book](https://github.com/yeeking/ai-enhanced-audio-book) itself — already graphed in this project's knowledge graph (`graphify-out/graph.json`), with `Part1_GettingStarted` through `Part4_NeuralFX` matching this chapter's structure directly.
