#include "PluginProcessor.h"
#include "PluginEditor.h"
#include <BinaryData.h>
#include <algorithm>
#include <sstream>

//==============================================================================
SteinmetzReverbAudioProcessor::SteinmetzReverbAudioProcessor()
    : AudioProcessor (BusesProperties()
                      .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                      .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      juce::Thread ("SteinmetzReverbWorker")
{
    addParameter (c1Param = new juce::AudioParameterFloat ("c1", "Conditioning 1", -1.0f, 1.0f, 0.5f));
    addParameter (c2Param = new juce::AudioParameterFloat ("c2", "Conditioning 2", -1.0f, 1.0f, -0.5f));

    std::string modelBytes (reinterpret_cast<const char*> (BinaryData::traced_reverb_88889_pt),
                             (size_t) BinaryData::traced_reverb_88889_ptSize);
    std::istringstream modelStream (modelBytes, std::ios::binary);
    reverbModel = torch::jit::load (modelStream);
    reverbModel.eval();

    startThread();
}

SteinmetzReverbAudioProcessor::~SteinmetzReverbAudioProcessor()
{
    signalThreadShouldExit();
    notify();
    stopThread (4000);
}

const juce::String SteinmetzReverbAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool SteinmetzReverbAudioProcessor::acceptsMidi() const
{
   #if JucePlugin_WantsMidiInput
    return true;
   #else
    return false;
   #endif
}

bool SteinmetzReverbAudioProcessor::producesMidi() const
{
   #if JucePlugin_ProducesMidiOutput
    return true;
   #else
    return false;
   #endif
}

bool SteinmetzReverbAudioProcessor::isMidiEffect() const
{
   #if JucePlugin_IsMidiEffect
    return true;
   #else
    return false;
   #endif
}

double SteinmetzReverbAudioProcessor::getTailLengthSeconds() const
{
    return (double) tailPad / currentSampleRate;
}

int SteinmetzReverbAudioProcessor::getNumPrograms()
{
    return 1;
}

int SteinmetzReverbAudioProcessor::getCurrentProgram()
{
    return 0;
}

void SteinmetzReverbAudioProcessor::setCurrentProgram (int index)
{
    juce::ignoreUnused (index);
}

const juce::String SteinmetzReverbAudioProcessor::getProgramName (int index)
{
    juce::ignoreUnused (index);
    return {};
}

void SteinmetzReverbAudioProcessor::changeProgramName (int index, const juce::String& newName)
{
    juce::ignoreUnused (index, newName);
}

void SteinmetzReverbAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    juce::ignoreUnused (samplesPerBlock);
    currentSampleRate = sampleRate;

    const juce::ScopedLock lock (queueLock);
    auto numChannels = (size_t) juce::jmax (getTotalNumInputChannels(), getTotalNumOutputChannels());
    channelStates.clear();
    channelStates.resize (numChannels);

    setLatencySamples (processChunkSize);
}

void SteinmetzReverbAudioProcessor::releaseResources()
{
}

bool SteinmetzReverbAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
     && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;

    return true;
}

std::vector<float> SteinmetzReverbAudioProcessor::processOneChunk (ChannelState& state,
                                                                    const std::vector<float>& chunk,
                                                                    float c1, float c2)
{
    const int totalLength = headPad + processChunkSize + tailPad;

    auto inputTensor = torch::zeros ({ 1, 1, totalLength });
    auto inAccessor = inputTensor.accessor<float, 3>();
    for (int i = 0; i < headPad; ++i)
        inAccessor[0][0][i] = state.history[(size_t) i];
    for (int i = 0; i < processChunkSize; ++i)
        inAccessor[0][0][headPad + i] = chunk[(size_t) i];
    // positions [headPad + processChunkSize, totalLength) stay zero — the
    // model's own causal receptive field fills them with the reverb's tail.

    auto conditioning = torch::tensor ({ { { c1, c2 } } });
    torch::jit::Kwargs kwargs;
    kwargs["c"] = conditioning;
    std::vector<torch::jit::IValue> inputs { inputTensor };

    auto output = (reverbModel.forward (inputs, kwargs).toTensor() * 0.25f).contiguous();
    auto outAccessor = output.accessor<float, 3>();

    std::vector<float> wet ((size_t) processChunkSize);
    for (int i = 0; i < processChunkSize; ++i)
        wet[(size_t) i] = outAccessor[0][0][headPad + i] + state.tail[(size_t) i];

    std::vector<float> newTail ((size_t) tailPad, 0.0f);
    for (int i = 0; i < tailPad; ++i)
    {
        float carried = (i + processChunkSize < tailPad) ? state.tail[(size_t) (i + processChunkSize)] : 0.0f;
        newTail[(size_t) i] = carried + outAccessor[0][0][headPad + processChunkSize + i];
    }
    state.tail = std::move (newTail);

    std::rotate (state.history.begin(), state.history.begin() + processChunkSize, state.history.end());
    std::copy (chunk.begin(), chunk.end(), state.history.end() - processChunkSize);

    return wet;
}

void SteinmetzReverbAudioProcessor::run()
{
    while (! threadShouldExit())
    {
        bool didWork = false;

        for (auto& state : channelStates)
        {
            std::vector<float> chunk;
            {
                const juce::ScopedLock lock (queueLock);
                if (state.inputQueue.size() >= (size_t) processChunkSize)
                {
                    chunk.assign (state.inputQueue.begin(), state.inputQueue.begin() + processChunkSize);
                    state.inputQueue.erase (state.inputQueue.begin(), state.inputQueue.begin() + processChunkSize);
                }
            }

            if (chunk.empty())
                continue;

            didWork = true;

            if (! modelIsUsable.load())
            {
                const juce::ScopedLock lock (queueLock);
                for (auto sample : chunk)
                    state.outputQueue.push_back (sample);
                continue;
            }

            const float c1 = c1Param->get();
            const float c2 = c2Param->get();

            try
            {
                auto wet = processOneChunk (state, chunk, c1, c2);
                const juce::ScopedLock lock (queueLock);
                for (auto sample : wet)
                    state.outputQueue.push_back (sample);
            }
            catch (const c10::Error& e)
            {
                DBG ("Steinmetz reverb forward() threw, falling back to passthrough: " << e.what());
                modelIsUsable = false;
                const juce::ScopedLock lock (queueLock);
                for (auto sample : chunk)
                    state.outputQueue.push_back (sample);
            }
        }

        if (! didWork && ! threadShouldExit())
            wait (10);
    }
}

void SteinmetzReverbAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer,
                                                   juce::MidiBuffer& midiMessages)
{
    juce::ignoreUnused (midiMessages);
    juce::ScopedNoDenormals noDenormals;

    auto totalNumInputChannels  = getTotalNumInputChannels();
    auto totalNumOutputChannels = getTotalNumOutputChannels();

    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear (i, 0, buffer.getNumSamples());

    const int numSamples = buffer.getNumSamples();

    {
        const juce::ScopedLock lock (queueLock);
        for (int channel = 0; channel < totalNumInputChannels && channel < (int) channelStates.size(); ++channel)
        {
            auto* input = buffer.getReadPointer (channel);
            auto& state = channelStates[(size_t) channel];
            for (int i = 0; i < numSamples; ++i)
                state.inputQueue.push_back (input[i]);
        }
    }

    notify();

    const juce::ScopedLock lock (queueLock);
    for (int channel = 0; channel < totalNumOutputChannels && channel < (int) channelStates.size(); ++channel)
    {
        auto* output = buffer.getWritePointer (channel);
        auto& state = channelStates[(size_t) channel];

        int i = 0;
        for (; i < numSamples && ! state.outputQueue.empty(); ++i)
        {
            output[i] = state.outputQueue.front();
            state.outputQueue.pop_front();
        }
        for (; i < numSamples; ++i)
            output[i] = 0.0f;
    }
}

bool SteinmetzReverbAudioProcessor::hasEditor() const
{
    return true;
}

juce::AudioProcessorEditor* SteinmetzReverbAudioProcessor::createEditor()
{
    return new SteinmetzReverbAudioProcessorEditor (*this);
}

void SteinmetzReverbAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    juce::MemoryOutputStream stream (destData, true);
    stream.writeFloat (c1Param->get());
    stream.writeFloat (c2Param->get());
}

void SteinmetzReverbAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    juce::MemoryInputStream stream (data, (size_t) sizeInBytes, false);
    if (stream.getNumBytesRemaining() >= (int) (2 * sizeof (float)))
    {
        *c1Param = stream.readFloat();
        *c2Param = stream.readFloat();
    }
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new SteinmetzReverbAudioProcessor();
}
