# yee-king-ai-audio-plugins
- **yee-king-ai-audio-plugins** (`.claude/skills/yee-king-ai-audio-plugins/SKILL.md`) — knowledge base from *Build AI-Enhanced Audio Plugins with C++* by Matthew John Yee-King. Covers JUCE plugin development, libtorch/RTNeural neural audio effects, interactive machine learning (meta-controller/Wekinator-style), variable-order Markov sequence modeling, and classical DSP (FIR/IIR/waveshaping).
Use this skill whenever working on JUCE plugin code, neural audio effects (LSTM/RTNeural/TorchScript), interactive ML control mappings, Markov-based sequencing, or classical DSP filters/waveshapers in this project — load the relevant chapter via its Chapter Index or Topic Index rather than re-deriving the theory from scratch.

## Optional add-ons (not included in this repo)

Not required for generating or building JUCE plugins — clone separately if wanted:
- **JUCE class-docs MCP servers**: [danielraffel/juce-docs-mcp-server](https://github.com/danielraffel/juce-docs-mcp-server) (TypeScript/Node) and [stefbil/JuceMCP-for-agents](https://github.com/stefbil/JuceMCP-for-agents) (Python) — both give an agent lookup access to JUCE class documentation.
- **ai-enhanced-audio-book**: [yeeking/ai-enhanced-audio-book](https://github.com/yeeking/ai-enhanced-audio-book) — the book's raw source/example code; already distilled into the `yee-king-ai-audio-plugins` skill above.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
