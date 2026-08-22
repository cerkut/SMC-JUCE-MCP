# Chapter 24: Modelling note duration

## Core Idea
Adds a third independent Markov model — note duration — by tracking per-note-number onset times, computing `noteOffTime - noteOnTime` on note-off, and using generated durations to set note-off scheduling instead of a hardcoded 1-second length.

## Frameworks Introduced
- **Design decision: independent models vs. compound state**: the author explicitly chooses to model pitch, IOI, and duration as *three separate* Markov models rather than one compound state combining all three. Rationale given: it lets duration patterns associate with pitch patterns not actually correlated in the training data — a deliberate creative choice, flagged as *not* "technically perfect" sequence modeling.

## Key Concepts
- **`message.getTimeStamp()` vs. `elapsedSamples`**: `elapsedSamples` only updates once per `processBlock` call, but a note-on can occur anywhere within that block — always add the message's own timestamp (0 to block-size) to `elapsedSamples` for the true sample-accurate time.
- **Per-note onset tracking**: `unsigned long noteOnTimes[127]` — same shape as the `noteOffTimes` array from Ch.22, storing when each note started so its duration can be computed on note-off.
- **Quantization trade-off**: raw (unquantized) live-played timing produces mostly unique IOI/duration values → sparse, low-order models. Quantizing to a grid increases repeated values → richer, higher-order models, at the cost of "robotic" timing. Left as an open design choice.

## Code Examples
```cpp
// tracking onset, computing duration on note-off
void MidiMarkovProcessor::analyseDuration(const juce::MidiBuffer& midiMessages) {
    for (const auto metadata : midiMessages) {
        auto message = metadata.getMessage();
        if (message.isNoteOn()) {
            noteOnTimes[message.getNoteNumber()] = elapsedSamples + message.getTimeStamp();
        }
        if (message.isNoteOff()) {
            unsigned long noteOffTime = elapsedSamples + message.getTimeStamp();
            unsigned long noteLength = noteOffTime - noteOnTimes[message.getNoteNumber()];
            noteDurationModel.putEvent(std::to_string(noteLength));
        }
    }
}
```
```cpp
// using the model's output instead of a hardcoded note-off time
unsigned int duration = std::stoi(noteDurationModel.getEvent(true));
noteOffTimes[note] = elapsedSamples + duration;   // was: elapsedSamples + getSampleRate()
```
- **What it demonstrates**: the exact same put/get Markov pattern as pitch (Ch.22) and IOI (Ch.23), applied to a third independent musical dimension — reinforcing that `MarkovManager` is a generic sequence-modeling tool, not pitch-specific.

## Anti-patterns
- Modeling raw, unquantized live-played durations/IOIs without considering their effect on model richness — every value tends to be slightly different, so the model stays stuck at low order (few repeated compound states) unless quantized.

## Key Takeaways
1. `processBlock` now runs three parallel analysis functions (`analysePitches`, `analyseDuration`, `analyseIoI`) — each independently modularized, each with its own `MarkovManager`.
2. Note duration replaces the Ch.22 hardcoded "1 second" note-off with a modeled, generated value.
3. Separate-models-vs-compound-state is an open design trade-off, not a settled answer — the author flags it explicitly for the reader to experiment with.
4. Quantization is a lever for model richness (more repeated states → higher achievable order) traded against "robotic" timing feel.

## Connects To
- **Ch 22-23**: reuses the same onset-tracking-array and buffer-swap patterns for a third musical dimension.
- **Ch 25**: the polyphonic extension that finally has to reconcile pitch+IOI+duration modeling with simultaneous notes.
