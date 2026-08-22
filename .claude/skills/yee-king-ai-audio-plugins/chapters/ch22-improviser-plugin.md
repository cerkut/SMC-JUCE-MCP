# Chapter 22: Starting the Improviser plugin

## Core Idea
Wires MIDI input → `MarkovManager::putEvent` (pitch model) → `getEvent` generation → MIDI output, plus the note-off scheduling pattern needed because `processBlock` only gives one short time window per call — the foundational plumbing every later Improviser chapter (IOI, duration, polyphony) reuses.

## Key Concepts
- **Store-then-process MIDI pattern**: don't let UI-thread MIDI (on-screen keyboard clicks) touch the model directly — buffer it (`juce::MidiBuffer midiToProcess`) and merge into `processBlock`'s own `midiMessages` buffer at the top of the function. "Do not let the user mess with your audio processor — only do it on your terms."
- **Where the model lives**: `MarkovManager` belongs in the **processor**, not the editor — only the processor has sample-accurate timing, persists for the plugin's lifetime, and receives host-originated MIDI directly.
- **Separate output buffer for generated notes**: build generated MIDI into a *temporary* `juce::MidiBuffer generatedMessages`, only `midiMessages.clear()` + re-add at the end — otherwise you can't cleanly avoid parroting input notes back out.
- **Note-off scheduling via a lookup array**: `unsigned long noteOffTimes[127]` (one slot per MIDI note) + a running `elapsedSamples` counter. On note-on, set `noteOffTimes[note] = elapsedSamples + getSampleRate()` ("1 second from now"); each `processBlock` call, scan the array for any note whose time has passed and emit its note-off. This buffer-granularity (not sample-accurate) timing recurs in every later timing chapter.

## Code Examples
```cpp
// merge UI-thread MIDI into processBlock's buffer, once per call
if (midiToProcess.getNumEvents() > 0) {
    midiMessages.addEvents(midiToProcess, midiToProcess.getFirstEventTime(),
                            midiToProcess.getLastEventTime() + 1, 0);
    midiToProcess.clear();
}
```
```cpp
// feed note-ons into the pitch model
for (const auto metadata : midiMessages) {
    auto message = metadata.getMessage();
    if (message.isNoteOn()) {
        pitchModel.putEvent(std::to_string(message.getNoteNumber()));
    }
}
```
```cpp
// generate a replacement note-on, buffered separately from the input
juce::MidiBuffer generatedMessages;
if (midiMessages.getNumEvents() > 0) {
    int note = std::stoi(pitchModel.getEvent(true));   // true = needChoices
    generatedMessages.addEvent(juce::MidiMessage::noteOn(1, note, 0.5f), 0);
    noteOffTimes[note] = elapsedSamples + getSampleRate();  // schedule note-off ~1s later
}
midiMessages.clear();
midiMessages.addEvents(generatedMessages, generatedMessages.getFirstEventTime(), -1, 0);

// each processBlock call: fire any due note-offs
for (auto i = 0; i < 127; ++i) {
    if (noteOffTimes[i] > 0 && noteOffTimes[i] < elapsedSamples) {
        generatedMessages.addEvent(juce::MidiMessage::noteOff(1, i, 0.0f), 0);
        noteOffTimes[i] = 0;
    }
}
elapsedSamples += buffer.getNumSamples();   // advance the clock, once per block
```
- **What it demonstrates**: the full input→model→generation→scheduled-note-off pipeline, buffer-granularity timing (not sample-accurate, but "good enough — worst case one buffer length off").

## Anti-patterns
- Feeding MIDI from the UI thread straight into the audio processor without buffering — breaks the audio-thread-safety discipline; always buffer and merge at a controlled point in `processBlock`.
- Sending a note-on every single `processBlock` call — at 44.1kHz/1024 samples that's ~43 calls/sec; without an explicit trigger condition (e.g. "only on receiving a note"), the plugin floods notes.
- Sending note-on and note-off in the same `processBlock` call — produces near-zero-length notes some synths ignore; schedule the note-off for a later call instead.
- Writing generated notes directly into the incoming `midiMessages` buffer — you lose the ability to `clear()` and replace with only your own generated notes (would "parrot" input back).

## Key Takeaways
1. Buffer UI-thread MIDI; only merge/process it inside `processBlock`, on your own schedule.
2. `MarkovManager` lives in the processor (sample-accurate timing, persists across UI recreation, receives host MIDI directly).
3. Note-off timing needs a per-note scheduled-time array (`noteOffTimes[127]`) plus a running sample counter — this pattern is reused for every later timing-related Improviser feature.
4. Generated notes go in a *separate* buffer, cleared and swapped into `midiMessages`, not appended alongside the input.

## Connects To
- **Ch 21**: the `MarkovManager` API (`putEvent`/`getEvent`/`getOrderOfLastEvent`) used here unmodified.
- **Ch 23-24**: this note-off timing array becomes the basis for measuring IOI and note duration.
- **Ch 25**: polyphonic extension of this same single-note pipeline.
