# Chapter 20: Background: all about sequencers

## Core Idea
Establishes the theory behind the Improviser: the **variable-order Markov model** — combining multiple fixed-order models to get both the "musical awareness" of higher orders and the output variety of lower orders, plus a specific order-reduction trick to escape repetitive-loop states.

## Frameworks Introduced
- **State, transition, observation**: a Markov model treats each item in a sequence as a *state*; the item that follows is the *observation*; tallying observation frequencies per state gives a *state transition matrix* of probabilities.
- **Order**: 0th-order = flat distribution over all observed states (no history); 1st-order = next-state distribution conditioned on 1 previous state; Nth-order conditions on the last N items concatenated into one compound state. Higher order → more "musically aware" but fewer observations per state (sparser, less varied).
- **Variable-order Markov model**: builds matrices at *several* orders simultaneously; generation prefers the highest order with data available, and **falls back to a lower order** when the current compound state has no observations (or only one, to avoid getting stuck).

## Key Concepts
- **Why Markov over neural nets here**: the author explicitly chooses Markov models for the Improviser (not because neural nets can't do it) because Markov models are computationally cheap enough to train *live, in real time*, from a single short performance — and musicians report feeling their own presence in the generated output.
- **Repetitive-loop avoidance rule**: if a state's transition row has ≤1 possible next observation, drop to a lower order and resample — prevents the generator collapsing into an infinite repeat of one note/chord.

## Reference Tables
| Order | Definition | Trade-off |
|---|---|---|
| 0th | flat distribution over all states | max variety, zero context awareness |
| 1st | next state given 1 previous state | some context, decent variety |
| Nth | next state given N previous states | strong context, sparse/low-variety data |
| Variable | combine several orders, fall back on sparse/degenerate rows | best of both, more complex generation logic |

## Anti-patterns
- Using a single fixed high order — musically "smarter" but prone to getting stuck repeating the same note/chord when a compound state has only one recorded continuation.
- Assuming higher order is strictly better — it trades away output variety for context-awareness; the variable-order combination exists specifically to avoid this trade-off.

## Key Takeaways
1. Variable-order Markov modeling = build matrices at multiple orders, prefer the highest order with enough data, degrade to lower orders on sparse/degenerate states.
2. The "reduce order and resample" rule triggers both on *zero* observations and on *exactly one* observation (to dodge repetitive loops), not just on missing data.
3. Markov models were chosen for real-time, small-dataset, live-performance learning — a deliberate trade-off versus neural nets, not a technical limitation.

## Connects To
- **Ch 21**: implements this exact variable-order algorithm in C++ via `MarkovModelCPP`.
- **Ch 22-25**: apply variable-order Markov modeling to pitch, IOI, duration, and polyphonic states in the actual Improviser plugin.
