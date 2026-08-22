#pragma once

#include "PluginProcessor.h"
#include <juce_audio_processors/juce_audio_processors.h>

//==============================================================================
class SteinmetzReverbAudioProcessorEditor : public juce::AudioProcessorEditor,
                                             private juce::Timer
{
public:
    explicit SteinmetzReverbAudioProcessorEditor (SteinmetzReverbAudioProcessor&);
    ~SteinmetzReverbAudioProcessorEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;

private:
    void timerCallback() override;

    SteinmetzReverbAudioProcessor& processorRef;

    juce::Slider c1Slider, c2Slider;
    juce::Label c1Label { {}, "Conditioning 1" };
    juce::Label c2Label { {}, "Conditioning 2" };
    juce::Label statusLabel;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SteinmetzReverbAudioProcessorEditor)
};
