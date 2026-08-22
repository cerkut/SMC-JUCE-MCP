# Chapter 18: Show a plugin's user interface

## Core Idea
Pops the hosted plugin's own editor UI into a separate `PluginWindow` (a `DocumentWindow`) rather than embedding it in the host's main window, and wires up proper close-button handling via a custom listener interface — deliberately choosing indirection over the "obvious but wrong" approach.

## Key Concepts
- **`AudioProcessorEditor` is a `Component`**: technically embeddable directly in your own UI — but the book explicitly advises against it (odd component lifetime, mismatched aesthetics/sizing).
- **`createEditorIfNeeded()`**: preferred over raw `createEditor()` — only creates a new editor instance if one doesn't already exist.
- **Bare pointer from a `unique_ptr`-owned object**: `pluginNode->getProcessor()` returns a raw pointer into memory the *node* owns — never call `delete` on it yourself.
- **Abstract class as a forced-implementation contract**: `virtual void pluginCloseButtonClicked() = 0;` (the `= 0`) makes `PluginWindowListener` uninstantiable directly — any subclass MUST implement it. Same pattern JUCE itself uses for `Button::Listener`.

## Code Examples
```cpp
// getting the hosted plugin's editor
juce::AudioProcessorEditor* PluginHostProcessor::getHostedPluginEditor() {
    if (pluginNode) return pluginNode->getProcessor()->createEditorIfNeeded();
    return nullptr;
}
```
```cpp
// PluginWindow: a DocumentWindow that owns the plugin's editor Component
PluginWindow::PluginWindow(juce::AudioProcessorEditor* editor)
    : DocumentWindow("plugin UI",
        juce::LookAndFeel::getDefaultLookAndFeel().findColour(juce::ResizableWindow::backgroundColourId),
        juce::DocumentWindow::minimiseButton | juce::DocumentWindow::closeButton) {
    setSize(400, 300);
    if (editor) {
        setContentOwned(editor, true);
        setResizable(editor->isResizable(), false);
    }
    setTopLeftPosition(100, 100);
    setVisible(true);
}
```
```cpp
// custom listener interface for the close button (abstract class pattern)
class PluginWindowListener {
public:
    virtual void pluginCloseButtonClicked() = 0;   // pure virtual: forces implementation
};
// PluginWindow notifies its listener on close:
void PluginWindow::closeButtonPressed() {
    if (listener) listener->pluginCloseButtonClicked();
}
// PluginHostEditor implements it, and deletes the window on close:
void PluginHostEditor::pluginCloseButtonClicked() {
    pluginWindow.reset();   // triggers unique_ptr-owned object's destruction
}
```
- **What it demonstrates**: separate-window UI hosting + the pure-virtual-listener pattern for propagating a close event back to the editor that owns the window's `unique_ptr`.

## Anti-patterns
- Embedding a hosted plugin's `AudioProcessorEditor` directly into your own main window's component tree — mismatched sizing/lifetime/aesthetics; use a separate `PluginWindow` instead.
- Manually `delete`-ing a raw pointer obtained from `pluginNode->getProcessor()` — that memory is owned by the graph node, not you.

## Key Takeaways
1. Host a plugin's UI in its own `DocumentWindow`, not embedded directly in your main window.
2. `createEditorIfNeeded()` avoids duplicate editor instances.
3. A pure-virtual listener interface (`= 0`) is how JUCE code (and this book) propagates events like window-close back to an owner across class boundaries.
4. `pluginWindow.reset()` is the correct way to destroy a `unique_ptr`-owned window from a listener callback.

## Connects To
- **Ch 16-17**: this UI-display capability builds on the plugin-hosting/graph mechanism from those chapters.
- **Ch 19**: the completed meta-controller keeps this "show plugin UI" button alongside its neural-net training controls.
