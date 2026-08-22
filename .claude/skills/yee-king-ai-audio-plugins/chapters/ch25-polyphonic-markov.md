# Chapter 25: Polyphonic Markov model

## Core Idea
Extends the Improviser to chords by encoding note-vectors as hyphen-delimited strings for the Markov model, using a `ChordDetector` (time-threshold grouping) to decide which near-simultaneous notes belong to the same chord, and adds a velocity model — completing the Improviser's modeled dimensions (pitch, IOI, duration, velocity).

## Frameworks Introduced
- **Polyphonic state encoding**: `notesToMarkovState({76,77,79}) -> "76-77-79-"`; `markovStateToNotes("76-77-79-")` tokenizes on `-` back to a vector. Polyphonic states are "just another type of state" to the Markov model — no algorithm change needed, only representation.
- **`ChordDetector`**: groups near-simultaneous note-ons into one chord using a configurable time threshold (~50ms found to work for human playing) — because real MIDI keyboard chords never arrive at exactly the same sample time, and may even land in different `processBlock` calls.

## Key Concepts
- **Why timestamp-equality doesn't work for chord detection**: human-played chords can have 30-40 sample (~0.3ms) timing spread between notes, and can straddle multiple `processBlock` calls at small buffer sizes — a threshold-based accumulator (`ChordDetector`) is needed instead of exact-timestamp matching.
- **Shared duration/velocity across a chord's notes**: when generating a chord, all notes in it get the *same* duration (from one `noteDurationModel.getEvent()` call) — pulling a separate duration per note would over-sample the model and distort the durations it actually learned.
- **Play-only / learning toggle** (left as an exercise): gate whether `putEvent` gets called on the models, so a trained model can generate without further modification once its state transition matrices are "good enough."

## Code Examples
```cpp
// encoding/decoding polyphonic states
std::string notesToMarkovState(const std::vector<int>& notesVec) {
    std::string state{""};
    for (const int& note : notesVec) state += std::to_string(note) + "-";
    return state;
}
std::vector<int> markovStateToNotes(const std::string& notesStr) {
    std::vector<int> notes{};
    if (notesStr == "0") return notes;
    for (const std::string& note : MarkovChain::tokenise(notesStr, '-'))
        notes.push_back(std::stoi(note));
    return notes;
}
```
```cpp
// feeding chord-grouped notes into the pitch model
chordDetect.addNote(message.getNoteNumber(), elapsedSamples + message.getTimeStamp());
if (chordDetect.hasChord()) {
    std::string notes = notesToMarkovState(chordDetect.getChord());
    pitchModel.putEvent(notes);
}
```
```cpp
// generating a chord: one shared duration/velocity for all its notes
std::string notes = pitchModel.getEvent();
unsigned int duration = std::stoi(noteDurationModel.getEvent(true));
juce::uint8 velocity = std::stoi(velocityModel.getEvent(true));
for (const int& note : markovStateToNotes(notes)) {
    generatedMessages.addEvent(juce::MidiMessage::noteOn(1, note, velocity), 0);
    noteOffTimes[note] = elapsedSamples + duration;
}
```
- **What it demonstrates**: chords are handled by changing *representation* (strings of notes) rather than the Markov algorithm; velocity is added as a fourth model using the exact same put/get pattern as pitch/IOI/duration.

## Anti-patterns
- Detecting chords by comparing exact note-on timestamps — real human playing never produces exactly-equal timestamps; use a threshold-based detector instead.
- Pulling an independent duration per note in a chord — over-samples the duration model and distorts learned durations; pull one duration and apply it to the whole chord.

## Key Takeaways
1. Polyphony is a representation change (vector → hyphen-delimited string state), not an algorithm change — the same variable-order Markov model handles it unmodified.
2. `ChordDetector`'s time threshold (~50ms) is a tunable parameter, not a hardcoded constant — different players/instruments may need different values.
3. The improviser now models four independent dimensions: pitch(-chord), IOI, duration, velocity — each its own `MarkovManager`, following the exact same put/get pattern throughout.
4. A play-only/learning-toggle is a natural next feature (not implemented in the book) for using a trained model without further mutating it.

## Connects To
- **Ch 22-24**: extends the monophonic pitch/IOI/duration pipeline built there to polyphonic states.
- **Ch 20-21**: the variable-order Markov theory and `MarkovManager` API this chapter's chord encoding still relies on unchanged.
- **Ch 39**: repo-guide examples 39.4.6-39.4.8 provide working polyphonic-modeller checkpoints.
