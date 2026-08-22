# Chapter 21: Programming with Markov models

## Core Idea
Hands-on introduction to the author's own `MarkovModelCPP` library via `MarkovManager`: feed in a sequence with `putEvent`, inspect the model with `getModelAsString`, and generate new sequences with `getEvent` — the reusable API every later Improviser chapter builds on.

## Key Concepts
- **`state_single` = `std::string`**: any string can be a Markov symbol — letters, note names with accidentals (`"C#"`), rests (`"-"`), words, anything.
- **`getModelAsString()` format**: `order,state,:count,observations` per line — e.g. `2,A,B,:1,C` means "the 2nd-order state (A,B) was followed by C once."
- **`getEvent()`**: generates the next symbol using the variable-order algorithm from Ch.20 — automatically finds the highest usable order.
- **`getOrderOfLastEvent()`**: reports which order was actually used for the last generated event — varies as the generation-side "memory" grows.
- **`needChoices` flag on `getEvent`**: `true` (default behavior) restricts sampling to states with ≥2 possible next observations (avoids repetitive loops, per Ch.20); `false` allows single-choice rows too — trades variety for higher achievable order.
- **`maxOrder` constructor parameter**: controls how many orders `MarkovManager` tracks internally.

## Code Examples
```cpp
// build a model from a sequence
MarkovManager mm{};
mm.putEvent("A");
mm.putEvent("B");
mm.putEvent("A");
mm.putEvent("C");
std::cout << mm.getModelAsString() << std::endl;
// -> 1,A,:2,B,C,
//    1,B,:1,A,
//    2,A,B,:1,A,
//    2,B,A,:1,C,
//    3,A,B,A,:1,C,
```
```cpp
// generate a sequence, watching the order used at each step
for (auto i = 0; i < 5; ++i) {
    state_single next = mm.getEvent();
    int order = mm.getOrderOfLastEvent();
    std::cout << "Next state " << next << " order " << order << std::endl;
}
```
```cpp
// musical symbols work the same way as letters
mm.putEvent("A"); mm.putEvent("B"); mm.putEvent("C#");
mm.putEvent("A"); mm.putEvent("B"); mm.putEvent("A");
mm.putEvent("C#"); mm.putEvent("-"); mm.putEvent("G#");
```
- **What it demonstrates**: symbols are opaque strings to the model — musical note names, rests, and plain letters are treated identically, which is why the same `MarkovManager` reused unmodified for pitch/duration/IOI modeling in later chapters.

## Anti-patterns
- Interpreting `getOrderOfLastEvent()`'s rising trend as a bug — it's expected: the generation-side memory grows as more events are generated, allowing progressively higher-order queries.
- Assuming `needChoices=false` gives "better" output — it increases achievable order but explicitly *reduces* variety (reintroduces the repetitive-loop risk Ch.20 warned about).

## Key Takeaways
1. `putEvent`/`getEvent`/`getModelAsString`/`getOrderOfLastEvent` is the entire `MarkovManager` API surface used throughout the Improviser.
2. Symbols are just strings — the same code path handles letters, musical note names, or any other tokenized sequence.
3. `needChoices` is the direct code-level control for the variety-vs-order trade-off described theoretically in Ch.20.

## Connects To
- **Ch 20**: the variable-order theory this chapter's API directly implements.
- **Ch 22-25**: `MarkovManager` reused as-is for pitch (22), IOI/duration (23-24), and polyphonic states (25) in the actual Improviser plugin.
