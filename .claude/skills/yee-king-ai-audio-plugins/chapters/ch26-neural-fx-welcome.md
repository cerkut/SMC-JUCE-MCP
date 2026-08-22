# Chapter 26: Welcome to neural effects

## Core Idea
Frames neural audio effects as the natural continuation of a 4-era history of audio effects (mechanical/tape → electro-mechanical → analogue → DSP), then a 5th "neural effects" era starting ~2013 with vacuum-tube amp modeling.

## Key Concepts
- **Wilmering et al.'s 4 eras of audio effects**: (1) mechanical/tape manipulation (Stravinsky's phonograms, Stockhausen's tape splicing), (2) electro-mechanical (Leslie speaker, spring reverb), (3) analogue signal processing (filters, distortion, delay-line reverb), (4) digital signal processing (Eventide delays 1971 → VST 1996 → in-the-box production).
- **Neural effects era** (author's addition): began ~2013 (Covert & Livingston, vacuum-tube guitar amp modeling) — matured via Alec Wright/Eero-Pekka Damskagg (~2019, guitar amps) and Steinmetz/Martinez Ramirez (Queen Mary University, reverbs/compressors). Damskagg's work fed into Neural DSP's commercial hardware.
- **Differentiable DSP (DDSP)**: an alternative to pure neural modeling — embeds traditional DSP components *inside* a neural network so training only needs to learn the DSP components' parameters, giving the network "a head start" since it starts from components already shaped for that kind of transformation. Cited example: Kuznetsov/Parker/Esqueda (Native Instruments) for EQ/distortion.

## Anti-patterns
- None specific — this is a scene-setting historical chapter.

## Key Takeaways
1. Neural effects (this book's Part 4 subject) are positioned as era 5, following mechanical → electro-mechanical → analogue → DSP.
2. Two distinct technical approaches exist: pure neural network modeling (what the book implements) vs. differentiable DSP (DDSP, embedding known-good DSP structure into the network) — DDSP is mentioned but not implemented in this book.
3. Guitar amp/pedal emulation specifically is the book's chosen application domain for the rest of Part 4.

## Connects To
- **Ch 27-30**: the "DSP trinity" (FIR/IIR/waveshaping) that neural effects are ultimately trying to emulate or replace.
- **Ch 31-38**: the book's own implementation of a neural guitar amp emulator, situated in this "neural effects era."
