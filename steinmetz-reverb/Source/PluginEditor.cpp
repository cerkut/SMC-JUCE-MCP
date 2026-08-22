#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
SteinmetzReverbAudioProcessorEditor::SteinmetzReverbAudioProcessorEditor (SteinmetzReverbAudioProcessor& p)
    : AudioProcessorEditor (&p), processorRef (p)
{
    for (auto* slider : { &c1Slider, &c2Slider })
    {
        slider->setSliderStyle (juce::Slider::LinearHorizontal);
        slider->setTextBoxStyle (juce::Slider::TextBoxRight, false, 60, 20);
        slider->setRange (-1.0, 1.0, 0.01);
        addAndMakeVisible (slider);
    }

    c1Slider.setValue (processorRef.c1Param->get(), juce::dontSendNotification);
    c2Slider.setValue (processorRef.c2Param->get(), juce::dontSendNotification);

    c1Slider.onValueChange = [this] { *processorRef.c1Param = (float) c1Slider.getValue(); };
    c2Slider.onValueChange = [this] { *processorRef.c2Param = (float) c2Slider.getValue(); };

    for (auto* label : { &c1Label, &c2Label })
    {
        label->setColour (juce::Label::textColourId, juce::Colours::white);
        addAndMakeVisible (label);
    }

    statusLabel.setJustificationType (juce::Justification::centred);
    statusLabel.setColour (juce::Label::textColourId, juce::Colours::lightgrey);
    addAndMakeVisible (statusLabel);

    setSize (420, 260);
    startTimerHz (2);
    timerCallback();
}

SteinmetzReverbAudioProcessorEditor::~SteinmetzReverbAudioProcessorEditor()
{
}

void SteinmetzReverbAudioProcessorEditor::paint (juce::Graphics& g)
{
    g.fillAll (getLookAndFeel().findColour (juce::ResizableWindow::backgroundColourId));

    g.setColour (juce::Colours::white);
    g.setFont (18.0f);
    g.drawFittedText ("Steinmetz Neural Reverb", getLocalBounds().removeFromTop (40),
                       juce::Justification::centred, 1);
}

void SteinmetzReverbAudioProcessorEditor::resized()
{
    auto area = getLocalBounds().reduced (20);
    area.removeFromTop (40); // title

    statusLabel.setBounds (area.removeFromBottom (30));
    area.removeFromBottom (10);

    auto row1 = area.removeFromTop (24);
    c1Label.setBounds (row1.removeFromLeft (120));
    c1Slider.setBounds (row1);

    area.removeFromTop (10);

    auto row2 = area.removeFromTop (24);
    c2Label.setBounds (row2.removeFromLeft (120));
    c2Slider.setBounds (row2);
}

void SteinmetzReverbAudioProcessorEditor::timerCallback()
{
    auto latencySeconds = (double) SteinmetzReverbAudioProcessor::getProcessChunkSize()
                          / juce::jmax (1.0, processorRef.getSampleRate());

    juce::String status = processorRef.isModelUsable()
        ? juce::String ("Model OK — ~") + juce::String (latencySeconds, 2) + " s buffering latency"
        : "Model failed — passing audio through unprocessed";

    statusLabel.setText (status, juce::dontSendNotification);
}
