#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "BinaryData.h"
#include <sstream>

//==============================================================================
DemoPluginAudioProcessor::DemoPluginAudioProcessor()
    : AudioProcessor (BusesProperties()
                      .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                      .withOutput ("Output", juce::AudioChannelSet::stereo(), true))
{
    // Load the TorchScript model from the binary data embedded at build time
    // (BinaryData::lstm_model_pt / _Size, from assets/lstm_model.pt) rather than
    // a hardcoded filesystem path — the book's own 036g_lstm-JUCE example hardcodes
    // an absolute path here, which only works on the author's machine.
    std::string modelBytes (reinterpret_cast<const char*> (BinaryData::lstm_model_pt),
                             (size_t) BinaryData::lstm_model_ptSize);
    std::istringstream modelStream (modelBytes, std::ios::binary);
    lstmModel = torch::jit::load (modelStream);
}

DemoPluginAudioProcessor::~DemoPluginAudioProcessor()
{
}

const juce::String DemoPluginAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool DemoPluginAudioProcessor::acceptsMidi() const
{
   #if JucePlugin_WantsMidiInput
    return true;
   #else
    return false;
   #endif
}

bool DemoPluginAudioProcessor::producesMidi() const
{
   #if JucePlugin_ProducesMidiOutput
    return true;
   #else
    return false;
   #endif
}

bool DemoPluginAudioProcessor::isMidiEffect() const
{
   #if JucePlugin_IsMidiEffect
    return true;
   #else
    return false;
   #endif
}

double DemoPluginAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int DemoPluginAudioProcessor::getNumPrograms()
{
    return 1;
}

int DemoPluginAudioProcessor::getCurrentProgram()
{
    return 0;
}

void DemoPluginAudioProcessor::setCurrentProgram (int index)
{
    juce::ignoreUnused (index);
}

const juce::String DemoPluginAudioProcessor::getProgramName (int index)
{
    juce::ignoreUnused (index);
    return {};
}

void DemoPluginAudioProcessor::changeProgramName (int index, const juce::String& newName)
{
    juce::ignoreUnused (index, newName);
}

void DemoPluginAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    juce::ignoreUnused (sampleRate);

    inBuffer.resize ((size_t) samplesPerBlock);
    outBuffer.resize ((size_t) samplesPerBlock);

    // One independent state per channel, shaped for whichever model is
    // currently loaded (lstmNumLayers/lstmHiddenSize — see loadModelFromFile).
    auto numChannels = (size_t) juce::jmax (getTotalNumInputChannels(), getTotalNumOutputChannels());
    lstmStates.resize (numChannels);
    for (auto& state : lstmStates)
        state = getRandomStartState (lstmNumLayers, lstmHiddenSize);
}

void DemoPluginAudioProcessor::releaseResources()
{
}

bool DemoPluginAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
     && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;

    return true;
}

void DemoPluginAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer,
                                              juce::MidiBuffer& midiMessages)
{
    juce::ignoreUnused (midiMessages);

    juce::ScopedNoDenormals noDenormals;
    auto totalNumInputChannels  = getTotalNumInputChannels();
    auto totalNumOutputChannels = getTotalNumOutputChannels();

    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear (i, 0, buffer.getNumSamples());

    // Pass each channel through the LSTM, retaining that channel's own state
    // between blocks (per-channel state avoids channel N's audio bleeding into
    // channel N+1's LSTM memory, unlike the book's single-shared-state example).
    for (int channel = 0; channel < totalNumInputChannels; ++channel)
    {
        auto* input = buffer.getReadPointer (channel);
        auto* output = buffer.getWritePointer (channel);

        if (! modelIsUsable.load())
        {
            // A previously-loaded model turned out to be incompatible after
            // all (see loadModelFromFile) — pass audio through unprocessed
            // rather than silence it or crash the host.
            if (input != output)
                std::copy (input, input + buffer.getNumSamples(), output);
            continue;
        }

        std::copy (input, input + inBuffer.size(), inBuffer.begin());

        try
        {
            lstmStates[(size_t) channel] = processBlockState (lstmModel, lstmStates[(size_t) channel],
                                                                inBuffer, outBuffer, buffer.getNumSamples());
        }
        catch (const c10::Error& e)
        {
            // Never let a torch exception escape into the host's audio thread.
            DBG ("LSTM forward() threw, falling back to passthrough: " << e.what());
            modelIsUsable = false;
            if (input != output)
                std::copy (input, input + buffer.getNumSamples(), output);
            continue;
        }

        std::copy (outBuffer.begin(), outBuffer.begin() + (std::ptrdiff_t) inBuffer.size(), output);
    }
}

bool DemoPluginAudioProcessor::hasEditor() const
{
    return true;
}

juce::AudioProcessorEditor* DemoPluginAudioProcessor::createEditor()
{
    return new DemoPluginAudioProcessorEditor (*this);
}

void DemoPluginAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    juce::ignoreUnused (destData);
}

void DemoPluginAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    juce::ignoreUnused (data, sizeInBytes);
}

//==============================================================================
// Path Helper Functions - Use macOS Application Support (no permission prompts)
//
// These functions provide standard paths for plugin data following Apple's
// Human Interface Guidelines. Using Application Support prevents permission
// dialogs during installation.
//
// Example usage:
//   auto samplesDir = DemoPluginAudioProcessor::getSamplesPath();
//   if (!samplesDir.exists())
//       samplesDir.createDirectory();
//

juce::File DemoPluginAudioProcessor::getApplicationSupportPath()
{
    auto appSupport = juce::File::getSpecialLocation(
        juce::File::userApplicationDataDirectory
    );

    auto projectFolder = appSupport.getChildFile(JucePlugin_Name);

    // Create if doesn't exist
    if (!projectFolder.exists())
        projectFolder.createDirectory();

    return projectFolder;
}

juce::File DemoPluginAudioProcessor::getSamplesPath()
{
    auto samplesDir = getApplicationSupportPath().getChildFile("Samples");

    if (!samplesDir.exists())
        samplesDir.createDirectory();

    return samplesDir;
}

juce::File DemoPluginAudioProcessor::getPresetsPath()
{
    auto presetsDir = getApplicationSupportPath().getChildFile("Presets");

    if (!presetsDir.exists())
        presetsDir.createDirectory();

    return presetsDir;
}

juce::File DemoPluginAudioProcessor::getUserDataPath()
{
    auto userDataDir = getApplicationSupportPath().getChildFile("UserData");

    if (!userDataDir.exists())
        userDataDir.createDirectory();

    return userDataDir;
}

juce::File DemoPluginAudioProcessor::getLogsPath()
{
    // Logs go to ~/Library/Logs/PluginName (standard macOS location)
    auto home = juce::File::getSpecialLocation(juce::File::userHomeDirectory);
    auto logsDir = home.getChildFile("Library").getChildFile("Logs").getChildFile(JucePlugin_Name);

    if (!logsDir.exists())
        logsDir.createDirectory();

    return logsDir;
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new DemoPluginAudioProcessor();
}

//==============================================================================
// 036g_lstm-JUCE LSTM state helpers (yee-king-ai-audio-plugins skill, ch33/37)

LSTMState DemoPluginAudioProcessor::getRandomStartState (int numLayers, int hiddenSize)
{
    torch::Tensor h0 = torch::randn ({ numLayers, hiddenSize });
    torch::Tensor c0 = torch::randn ({ numLayers, hiddenSize });
    return c10::ivalue::Tuple::create ({ h0, c0 });
}

LSTMState DemoPluginAudioProcessor::processBlockState (torch::jit::script::Module& model,
                                                         const LSTMState& state,
                                                         std::vector<float>& inBlock,
                                                         std::vector<float>& outBlock,
                                                         int numSamples)
{
    torch::Tensor in_t = torch::from_blob (inBlock.data(), { static_cast<int64_t> (numSamples) });
    in_t = in_t.view ({ -1, 1 });

    std::vector<torch::jit::IValue> inputs;
    inputs.push_back (in_t);
    inputs.push_back (state);

    torch::jit::IValue out_ival = model.forward (inputs);
    auto out_elements = out_ival.toTuple()->elements();
    torch::Tensor out_t = out_elements[0].toTensor().view ({ -1 });

    float* data_ptr = out_t.data_ptr<float>();
    std::copy (data_ptr, data_ptr + inBlock.size(), outBlock.begin());

    return out_elements[1].toTuple();
}

bool DemoPluginAudioProcessor::detectLstmShape (const torch::jit::script::Module& model,
                                                  int& numLayers, int& hiddenSize)
{
    numLayers = 0;
    hiddenSize = 0;

    for (const auto& param : model.named_parameters())
    {
        // A bare torch.nn.LSTM, scripted directly (no wrapping class/prefix),
        // names its per-layer params "weight_hh_l0", "weight_hh_l1", etc.
        // weight_hh_l<N> has shape [4 * hiddenSize, hiddenSize].
        if (param.name.find ("weight_hh_l") != std::string::npos)
        {
            auto sizes = param.value.sizes();
            if (sizes.size() == 2)
                hiddenSize = (int) sizes[1];
            ++numLayers;
        }
    }

    return numLayers > 0 && hiddenSize > 0;
}

bool DemoPluginAudioProcessor::loadModelFromFile (const juce::File& file, juce::String& errorMessage)
{
    if (! file.existsAsFile())
    {
        errorMessage = "File does not exist: " + file.getFullPathName();
        return false;
    }

    torch::jit::script::Module newModel;
    try
    {
        newModel = torch::jit::load (file.getFullPathName().toStdString());
    }
    catch (const c10::Error& e)
    {
        errorMessage = "Failed to load TorchScript model:\n" + juce::String (e.what());
        return false;
    }

    int numLayers = 1, hiddenSize = 1;
    if (! detectLstmShape (newModel, numLayers, hiddenSize))
    {
        // Fall back to the built-in model's shape; the test inference below
        // will catch it if that guess is wrong.
        numLayers = 1;
        hiddenSize = 1;
    }

    // Validate with a throwaway inference BEFORE committing to this model —
    // a shape/calling-convention mismatch (e.g. this is a ch37-style model
    // with a different forward() signature, not a bare traced torch.nn.LSTM)
    // would otherwise only surface the first time real audio arrives.
    {
        LSTMState testState = getRandomStartState (numLayers, hiddenSize);
        std::vector<float> testIn (64, 0.0f), testOut (64, 0.0f);
        try
        {
            processBlockState (newModel, testState, testIn, testOut, (int) testIn.size());
        }
        catch (const c10::Error& e)
        {
            errorMessage = "Model loaded but failed a test inference — likely an "
                            "incompatible architecture (this plugin only supports a bare "
                            "torch.nn.LSTM traced with explicit (input, (h0,c0)) state args, "
                            "matching yee-king-ai-audio-plugins skill ch32/33).\n" + juce::String (e.what());
            return false;
        }
    }

    // Swap the model in with processing suspended, so processBlock never sees
    // a half-updated model/state pair (same pattern as the book's plugin-host
    // loadPlugin, ch16-17, applied here to a model swap instead of a plugin).
    suspendProcessing (true);
    lstmModel = std::move (newModel);
    lstmNumLayers = numLayers;
    lstmHiddenSize = hiddenSize;
    for (auto& state : lstmStates)
        state = getRandomStartState (numLayers, hiddenSize);
    modelIsUsable = true;
    loadedModelName = file.getFileName();
    suspendProcessing (false);

    return true;
}
