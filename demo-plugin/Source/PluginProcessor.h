#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include <torch/script.h>
#include <atomic>

// LSTM hidden/cell state, threaded between processBlock calls so the network's
// memory survives across audio blocks instead of resetting every call (see
// yee-king-ai-audio-plugins skill, ch33/ch37 — "LSTM state must be threaded
// across audio blocks", and the book's 036g_lstm-JUCE example this is based on).
using LSTMState = c10::intrusive_ptr<c10::ivalue::Tuple>;

//==============================================================================
/**
*/
class DemoPluginAudioProcessor : public juce::AudioProcessor
{
public:
    DemoPluginAudioProcessor();
    ~DemoPluginAudioProcessor() override;

    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;

    bool isBusesLayoutSupported (const BusesLayout& layouts) const override;

    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override;

    const juce::String getName() const override;

    bool acceptsMidi() const override;
    bool producesMidi() const override;
    bool isMidiEffect() const override;
    double getTailLengthSeconds() const override;

    int getNumPrograms() override;
    int getCurrentProgram() override;
    void setCurrentProgram (int index) override;
    const juce::String getProgramName (int index) override;
    void changeProgramName (int index, const juce::String& newName) override;

    void getStateInformation (juce::MemoryBlock& destData) override;
    void setStateInformation (const void* data, int sizeInBytes) override;

    //==============================================================================
    // Path helpers - macOS Application Support paths (no permission prompts)
    static juce::File getApplicationSupportPath();
    static juce::File getSamplesPath();
    static juce::File getPresetsPath();
    static juce::File getUserDataPath();
    static juce::File getLogsPath();

    //==============================================================================
    // Load a different TorchScript LSTM model at runtime, replacing the
    // built-in assets/lstm_model.pt. IMPORTANT: this only supports models
    // using the SAME calling convention as the book's ch32/33 examples this
    // plugin is based on — a bare torch.nn.LSTM traced with an explicit
    // (input, (h0, c0)) state argument, returning (output, (h1, c1)). A model
    // exported the ch37 way (a custom class wrapping LSTM+Dense with state
    // handled internally, returning a plain tensor) will NOT work here — it
    // uses a different forward() signature entirely. On mismatch this returns
    // false with an explanatory message rather than crashing the audio thread.
    bool loadModelFromFile (const juce::File& file, juce::String& errorMessage);
    juce::String getLoadedModelName() const { return loadedModelName; }

private:
    //==============================================================================
    // 036g_lstm-JUCE neural audio effect (yee-king-ai-audio-plugins skill, ch32-33/37)
    //
    // The model is a tiny (1-hidden-unit), essentially untrained TorchScript LSTM —
    // pedagogically it demonstrates that even random LSTM weights measurably
    // distort/harmonically color a signal (ch32), not a real trained amp model.
    // Swap assets/lstm_model.pt for a properly trained model (ch34-37) for musical use.
    torch::jit::script::Module lstmModel;

    // One state per channel: the book's own example shares a single state across
    // all channels in its processBlock loop, which lets channel N's audio bleed
    // into channel N+1's LSTM memory. Keeping a state per channel avoids that.
    std::vector<LSTMState> lstmStates;
    std::vector<float> inBuffer;
    std::vector<float> outBuffer;

    // Architecture of the currently-loaded model (auto-detected on load; falls
    // back to 1/1, matching the built-in model, if detection fails).
    int lstmNumLayers = 1;
    int lstmHiddenSize = 1;
    juce::String loadedModelName { "Default (built-in, untrained demo model)" };

    // Set false if a real-time forward() call throws (e.g. a loaded model
    // turns out to be incompatible after all) — processBlock then falls back
    // to passing audio through unprocessed instead of crashing the host.
    std::atomic<bool> modelIsUsable { true };

    static LSTMState getRandomStartState (int numLayers, int hiddenSize);
    static LSTMState processBlockState (torch::jit::script::Module& model,
                                         const LSTMState& state,
                                         std::vector<float>& inBlock,
                                         std::vector<float>& outBlock,
                                         int numSamples);

    // Inspects a loaded module's own parameters to recover its LSTM's
    // (numLayers, hiddenSize) — looks for "weight_hh_l<N>" tensors (shape
    // [4*hiddenSize, hiddenSize]), the naming a plain torch.nn.LSTM produces
    // when scripted directly (no wrapping class/prefix).
    static bool detectLstmShape (const torch::jit::script::Module& model, int& numLayers, int& hiddenSize);

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (DemoPluginAudioProcessor)
};
