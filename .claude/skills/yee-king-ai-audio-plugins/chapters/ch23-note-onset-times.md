# Chapter 23: Modelling note onset times

## Core Idea
Adds a second Markov model — inter-onset-interval (IOI, time between note-ons) — alongside the pitch model, then uses generated IOIs to schedule *when* the improviser should play its next note instead of always echoing immediately.

## Key Concepts
- **IOI computation**: `exactNoteOnTime = elapsedSamples + message.getTimeStamp(); ioi = exactNoteOnTime - lastNoteOnTime;` — the gap between consecutive note-ons, fed into its own `MarkovManager` (`iOIModel`) as a separate model from pitch.
- **Bounding IOI values before modeling**: only add IOIs within `[0.05s, 2s]` (in samples) — unbounded long pauses would otherwise get modeled and later reproduced as awkward silences during a live performance.
- **Decoupling generation-time from receive-time**: `isTimeToPlayNote(currentTime)` compares `elapsedSamples` against a stored `modelPlayNoteTime`; only then is a note generated, and the *next* `modelPlayNoteTime` is set by querying `iOIModel.getEvent()` for a generated wait time — this is what turns "echo immediately" into "wait a modeled amount of time, then play."
- **Refactoring discipline**: `analyseIoI`, `analysePitches`, and `generateNotesFromModel` are split into their own functions with `const &` params — the chapter explicitly treats this as good practice once `processBlock` starts accumulating multiple concerns.

## Code Examples
```cpp
// computing and modeling IOI, with sanity bounds
unsigned long exactNoteOnTime = elapsedSamples + message.getTimeStamp();
unsigned long ioi = exactNoteOnTime - lastNoteOnTime;
if (ioi < getSampleRate() * 2 && ioi > getSampleRate() * 0.05) {
    iOIModel.putEvent(std::to_string(ioi));
}
lastNoteOnTime = exactNoteOnTime;
```
```cpp
// deciding WHEN to play, driven by a generated IOI
bool MidiMarkovProcessor::isTimeToPlayNote(unsigned long currentTime) {
    return currentTime >= modelPlayNoteTime;
}
// in generateNotesFromModel, once a note is played:
unsigned long nextIoI = std::stoi(iOIModel.getEvent());
if (nextIoI > 0) modelPlayNoteTime = elapsedSamples + nextIoI;
```
- **What it demonstrates**: two independent Markov models (pitch, IOI) driving two independent decisions (what note, when to play it) from the same MIDI input stream.

## Anti-patterns
- Modeling unbounded IOIs — a single long pause in the input gets faithfully reproduced as an awkward silence in generated output; always bound the range before `putEvent`.
- The **bootstrapping problem**: without a startup guard, the plugin endlessly generates notes even before it's received any real MIDI (since `modelPlayNoteTime` starts at 0 and immediately looks "due"). The book leaves the fix as an exercise: a boolean flag defaulting to "no MIDI received yet" that suppresses generation until real input arrives.
- Triggering all due notes at the very start of a block instead of at their correct sample offset within it — introduces up to one block-length of timing jitter (also left as a further-work item).

## Key Takeaways
1. IOI is modeled as its own independent Markov chain, separate from pitch — same `MarkovManager` API, different symbol domain (stringified sample counts).
2. Bound raw timing values before feeding a Markov model — unfiltered pauses degrade musicality.
3. "When to play" and "what to play" are decoupled: `isTimeToPlayNote` gates generation; the IOI model's output sets the *next* gate time.
4. Two known rough edges are left unresolved here: the generation-before-any-input bootstrapping bug, and block-boundary (vs. sample-accurate) note timing.

## Connects To
- **Ch 22**: reuses the note-off scheduling array and buffer-swap pattern from that chapter unchanged.
- **Ch 24**: adds a third Markov model (note duration) using the same pattern as IOI here.
- **Ch 25**: extends this monophonic pipeline to polyphonic (chord) states.
