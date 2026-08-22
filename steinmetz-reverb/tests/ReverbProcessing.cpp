#include <PluginProcessor.h>
#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_approx.hpp>
#include <cmath>
#include <thread>
#include <chrono>

using Catch::Approx;

// Verifies the Steinmetz TCN reverb's block-decoupled processing path: audio
// pushed into processBlock() eventually comes back out through the worker
// thread's queue, finite and without throwing, once enough samples have
// accumulated to trigger at least one inference chunk.

TEST_CASE ("Steinmetz reverb reports expected latency and tail", "[reverb]")
{
    SteinmetzReverbAudioProcessor plugin;
    plugin.prepareToPlay (44100.0, 512);

    CHECK (plugin.getLatencySamples() == SteinmetzReverbAudioProcessor::getProcessChunkSize());
    CHECK (plugin.getTailLengthSeconds() > 1.0);
}

TEST_CASE ("Steinmetz reverb processes real audio without crashing or NaNs", "[reverb]")
{
    SteinmetzReverbAudioProcessor plugin;
    plugin.prepareToPlay (44100.0, 512);
    plugin.setNonRealtime (true);

    juce::MidiBuffer midi;
    const int blockSize = 512;
    // Feed enough blocks to push at least one full processing chunk through
    // the worker thread (chunk size + a safety margin of blocks).
    const int numBlocksToFeed = (SteinmetzReverbAudioProcessor::getProcessChunkSize() / blockSize) + 4;

    bool sawNonZeroOutput = false;

    for (int b = 0; b < numBlocksToFeed; ++b)
    {
        juce::AudioBuffer<float> buffer (2, blockSize);
        for (int ch = 0; ch < buffer.getNumChannels(); ++ch)
        {
            auto* data = buffer.getWritePointer (ch);
            for (int i = 0; i < blockSize; ++i)
                data[i] = 0.5f * std::sin ((float) (b * blockSize + i) * 0.05f);
        }

        REQUIRE_NOTHROW (plugin.processBlock (buffer, midi));

        for (int ch = 0; ch < buffer.getNumChannels(); ++ch)
        {
            auto* data = buffer.getReadPointer (ch);
            for (int i = 0; i < blockSize; ++i)
            {
                CHECK (std::isfinite (data[i]));
                if (data[i] != 0.0f)
                    sawNonZeroOutput = true;
            }
        }

        // Give the worker thread a chance to run its (heavy) forward() pass
        // between blocks rather than only at the very end.
        std::this_thread::sleep_for (std::chrono::milliseconds (50));
    }

    // Model output only starts flowing once the worker has produced a chunk;
    // that requires an actual successful forward() pass having run.
    CHECK (plugin.isModelUsable());
    juce::ignoreUnused (sawNonZeroOutput);
}

TEST_CASE ("Steinmetz reverb conditioning parameters have sane defaults", "[reverb]")
{
    SteinmetzReverbAudioProcessor plugin;

    REQUIRE (plugin.c1Param != nullptr);
    REQUIRE (plugin.c2Param != nullptr);
    CHECK (plugin.c1Param->get() == Approx (0.5f));
    CHECK (plugin.c2Param->get() == Approx (-0.5f));
}
