#include <PluginProcessor.h>
#include <catch2/catch_test_macros.hpp>

// Verifies the "load another .ts model" feature added on top of the
// yee-king-ai-audio-plugins 036g_lstm-JUCE example. Uses two throwaway
// TorchScript files generated for this test run (see the session that added
// this test) rather than checked-in fixtures.

TEST_CASE ("Load a compatible LSTM model with a different hidden size", "[lstm]")
{
    DemoPluginAudioProcessor plugin;
    plugin.prepareToPlay (44100.0, 512);

    juce::String errorMessage;
    bool loaded = plugin.loadModelFromFile (juce::File ("/tmp/test_lstm_4units.ts"), errorMessage);

    INFO (errorMessage.toStdString());
    REQUIRE (loaded);
    CHECK (plugin.getLoadedModelName() == "test_lstm_4units.ts");

    // Run real audio through it to confirm the swapped-in model (with a
    // different hidden size than the built-in 1-unit model) actually works
    // end-to-end, not just that torch::jit::load() succeeded.
    juce::AudioBuffer<float> buffer (2, 512);
    for (int ch = 0; ch < buffer.getNumChannels(); ++ch)
    {
        auto* data = buffer.getWritePointer (ch);
        for (int i = 0; i < buffer.getNumSamples(); ++i)
            data[i] = std::sin ((float) i * 0.05f);
    }
    juce::MidiBuffer midi;

    REQUIRE_NOTHROW (plugin.processBlock (buffer, midi));

    // Output should be finite (no NaN/Inf from a shape mismatch slipping through).
    for (int ch = 0; ch < buffer.getNumChannels(); ++ch)
    {
        auto* data = buffer.getReadPointer (ch);
        for (int i = 0; i < buffer.getNumSamples(); ++i)
            CHECK (std::isfinite (data[i]));
    }
}

TEST_CASE ("Reject an incompatible model without crashing", "[lstm]")
{
    DemoPluginAudioProcessor plugin;
    plugin.prepareToPlay (44100.0, 512);

    auto nameBeforeAttempt = plugin.getLoadedModelName();

    juce::String errorMessage;
    bool loaded = plugin.loadModelFromFile (juce::File ("/tmp/test_incompatible.ts"), errorMessage);

    CHECK_FALSE (loaded);
    CHECK (errorMessage.isNotEmpty());
    // The built-in model should still be active — a failed load must not
    // leave the plugin in a half-swapped state.
    CHECK (plugin.getLoadedModelName() == nameBeforeAttempt);

    // The still-active built-in model should keep processing audio fine.
    juce::AudioBuffer<float> buffer (2, 512);
    buffer.clear();
    juce::MidiBuffer midi;
    REQUIRE_NOTHROW (plugin.processBlock (buffer, midi));
}

TEST_CASE ("Loading a missing file fails cleanly", "[lstm]")
{
    DemoPluginAudioProcessor plugin;
    plugin.prepareToPlay (44100.0, 512);

    juce::String errorMessage;
    bool loaded = plugin.loadModelFromFile (juce::File ("/tmp/does_not_exist_at_all.ts"), errorMessage);

    CHECK_FALSE (loaded);
    CHECK (errorMessage.isNotEmpty());
}
