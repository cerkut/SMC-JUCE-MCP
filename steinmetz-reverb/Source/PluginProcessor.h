#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include <torch/script.h>
#include <atomic>
#include <deque>
#include <vector>

// Steinmetz steerable neural reverb (arXiv:2112.02926): a causal TCN with a
// large receptive field. The model needs ~88888 samples of past context to
// compute one output sample, far more than any host processBlock() call
// provides — so audio in/out is decoupled from inference via queues, and the
// actual TCN forward() (too slow for the audio thread) runs on a worker
// thread. See PluginProcessor.cpp for the block-processing/overlap-add
// algorithm, ported from the book's 038a_neural_conv_steinmetz/main_block.cpp.
class SteinmetzReverbAudioProcessor : public juce::AudioProcessor,
                                       private juce::Thread
{
public:
    SteinmetzReverbAudioProcessor();
    ~SteinmetzReverbAudioProcessor() override;

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

    juce::AudioParameterFloat* c1Param = nullptr;
    juce::AudioParameterFloat* c2Param = nullptr;

    bool isModelUsable() const { return modelIsUsable.load(); }
    static constexpr int getProcessChunkSize() { return processChunkSize; }

private:
    // Matches the receptive field of assets/traced_reverb_88889.pt.
    static constexpr int receptiveField = 88889;
    static constexpr int headPad = receptiveField - 1;
    static constexpr int tailPad = receptiveField - 1;
    // Amortizes the ~180k-sample forward() pass over this many output samples.
    static constexpr int processChunkSize = 4096;

    torch::jit::script::Module reverbModel;
    std::atomic<bool> modelIsUsable { true };
    double currentSampleRate = 44100.0;

    struct ChannelState
    {
        std::vector<float> history = std::vector<float> ((size_t) headPad, 0.0f);
        std::vector<float> tail    = std::vector<float> ((size_t) tailPad, 0.0f);
        std::deque<float> inputQueue;
        std::deque<float> outputQueue;
    };

    std::vector<ChannelState> channelStates;
    // inputQueue/outputQueue are shared with processBlock(); history/tail are
    // only ever touched by the worker thread, so they need no locking.
    juce::CriticalSection queueLock;

    void run() override;
    std::vector<float> processOneChunk (ChannelState& state, const std::vector<float>& chunk, float c1, float c2);

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SteinmetzReverbAudioProcessor)
};
