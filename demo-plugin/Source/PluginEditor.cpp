#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
DemoPluginAudioProcessorEditor::DemoPluginAudioProcessorEditor (DemoPluginAudioProcessor& p)
    : AudioProcessorEditor (&p), processorRef (p)
{
    addAndMakeVisible (loadModelButton);
    loadModelButton.onClick = [this] { showLoadModelDialog(); };

    modelStatusLabel.setText ("Model: " + processorRef.getLoadedModelName(), juce::dontSendNotification);
    modelStatusLabel.setJustificationType (juce::Justification::centred);
    modelStatusLabel.setColour (juce::Label::textColourId, juce::Colours::white);
    addAndMakeVisible (modelStatusLabel);

    setSize (400, 300);
}

DemoPluginAudioProcessorEditor::~DemoPluginAudioProcessorEditor()
{
}

void DemoPluginAudioProcessorEditor::paint (juce::Graphics& g)
{
    g.fillAll (getLookAndFeel().findColour (juce::ResizableWindow::backgroundColourId));

    g.setColour (juce::Colours::white);
    g.setFont (15.0f);
    g.drawFittedText ("LSTM Neural Effect", getLocalBounds().removeFromTop (getHeight() - 90),
                       juce::Justification::centred, 1);
}

void DemoPluginAudioProcessorEditor::resized()
{
    auto area = getLocalBounds().reduced (10);
    modelStatusLabel.setBounds (area.removeFromBottom (40));
    loadModelButton.setBounds (area.removeFromBottom (30).reduced (60, 0));
}

void DemoPluginAudioProcessorEditor::showLoadModelDialog()
{
    modelChooser = std::make_unique<juce::FileChooser> (
        "Select a TorchScript (.ts) LSTM model",
        juce::File(),
        "*.ts;*.pt");

    constexpr auto flags = juce::FileBrowserComponent::openMode
                          | juce::FileBrowserComponent::canSelectFiles;

    modelChooser->launchAsync (flags, [this] (const juce::FileChooser& chooser)
    {
        auto file = chooser.getResult();
        if (! file.existsAsFile())
            return; // user cancelled

        juce::String errorMessage;
        if (processorRef.loadModelFromFile (file, errorMessage))
        {
            modelStatusLabel.setText ("Model: " + processorRef.getLoadedModelName(),
                                       juce::dontSendNotification);
        }
        else
        {
            juce::AlertWindow::showMessageBoxAsync (juce::AlertWindow::WarningIcon,
                                                     "Failed to load model", errorMessage);
        }
    });
}
