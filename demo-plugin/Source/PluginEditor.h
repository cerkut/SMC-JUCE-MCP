#pragma once

#include "PluginProcessor.h"
#include <juce_audio_processors/juce_audio_processors.h>

//==============================================================================
/**
*/
class DemoPluginAudioProcessorEditor : public juce::AudioProcessorEditor
{
public:
    explicit DemoPluginAudioProcessorEditor (DemoPluginAudioProcessor&);
    ~DemoPluginAudioProcessorEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;

private:
    DemoPluginAudioProcessor& processorRef;

    juce::TextButton loadModelButton { "Load Model (.ts)..." };
    juce::Label modelStatusLabel;
    std::unique_ptr<juce::FileChooser> modelChooser;

    void showLoadModelDialog();

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (DemoPluginAudioProcessorEditor)
};
