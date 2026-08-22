#pragma once

#include "PluginProcessor.h"
#include "Visage/JuceVisageBridge.h"
#include <juce_audio_processors/juce_audio_processors.h>
#include <visage_app/application_window.h>
#include <visage_widgets/frame.h>

class SteinmetzReverbAudioProcessorEditor : public juce::AudioProcessorEditor,
                                                    public juce::Timer
{
public:
    explicit SteinmetzReverbAudioProcessorEditor (SteinmetzReverbAudioProcessor&);
    ~SteinmetzReverbAudioProcessorEditor() override;

    void timerCallback() override;
    void resized() override;

private:
    void createVisageUI();
    void layoutChildren();

    SteinmetzReverbAudioProcessor& processorRef;

    std::unique_ptr<JuceVisageBridge> bridge;
    std::unique_ptr<visage::Frame> rootFrame;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SteinmetzReverbAudioProcessorEditor)
};
