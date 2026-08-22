# Chapter 37: Operationalising the model in a plugin

## Core Idea
Deploys a fully trained (not random) LSTM into the JUCE plugin from Ch.33, exporting via `torch.jit.script` (not `.trace`, since the model's internal state-handling logic needs script-level analysis, not just a traced execution path), and honestly reports that real-world performance falls well short of Ch.32's best-case benchmarks.

## Frameworks Introduced
- **`torch.jit.script` vs. `torch.jit.trace`**: tracing (used in Ch.32-33 for the raw `torch.nn.LSTM`) only records one concrete execution path — insufficient once the model class (`SimpleLSTM`) has its own `forward()` logic with internal state handling. `torch.jit.script(model)` analyzes the actual Python code, correctly capturing conditional/stateful logic a trace would miss.

## Key Concepts
- **Locating the best checkpoint**: `.pth` filenames encode epoch and validation loss (e.g. `lstm_size_32_epoch_3_loss_0.6968.pth`) — pick the lowest-loss file from the `runs/.../saved_models/` folder as your best model.
- **Loading + exporting a trained model**:
  ```python
  model = torch.load(saved_pth_path)
  model.eval()                        # switch to inference mode
  scripted_model = torch.jit.script(model)
  torch.jit.save(scripted_model, export_pt_path)
  ```
- **State is now internal to the model**: unlike Ch.33's raw `torch.nn.LSTM` (where you had to manually thread `LSTMState` between calls), `SimpleLSTM`'s own `forward()` handles state internally — the plugin code no longer manages an explicit state tuple.
- **3D input tensor for batched sequences**: `in_t.view({1, -1, 1})` (batch=1, sequence, channels=1) instead of Ch.33's 2D `view({-1, 1})` — because `SimpleLSTM` was designed to process batches of sequences (training-time shape), so inference wraps a single sequence in a batch of size 1.
- **Debug/Release build parity (again)**: on Windows, mismatching your plugin's build mode against the libtorch build mode causes a silent, undebuggable crash at `torch::jit::load`.
- **Real-world performance ≠ benchmark performance**: Ch.32's isolated benchmark suggested up to 128-256 hidden units real-time capable; running the *actual plugin* inside a real DAW (Reaper), even a 32-unit LSTM audibly glitches on the author's M1 Mac Mini (offline render: 0.2x real-time, though sonically correct) — while the same plugin runs fine on Linux/Intel. This performance gap is the direct motivation for RTNeural (Ch.38).

## Code Examples
```cpp
// plugin-side model + buffers
torch::jit::script::Module lstmModel;
std::vector<float> inBuffer, outBuffer;

// loading (with existence check to fail loudly, not silently)
std::string fp = modelFolder + "dist_32.ts";
if (!std::filesystem::exists(fp)) { DBG("File " << fp << " not found"); throw std::exception(); }
lstmModel = torch::jit::load(fp);
```
```cpp
// processBlockNN: 3D tensor shape, no manual state threading
void processBlockNN(torch::jit::script::Module& model,
                     std::vector<float>& inBlock, std::vector<float>& outBlock, int numSamples) {
    torch::Tensor in_t = torch::from_blob(inBlock.data(), {(int64_t)numSamples}).view({1, -1, 1});
    std::vector<torch::jit::IValue> inputs; inputs.push_back(in_t);
    torch::jit::IValue out_ival = model.forward(inputs);
    torch::Tensor out_t = out_ival.toTensor().view({-1});
    float* data_ptr = out_t.data_ptr<float>();
    std::copy(data_ptr, data_ptr + inBlock.size(), outBlock.begin());
}
```
```cpp
// prepareToPlay: size the transport buffers
inBuffer.resize((size_t)samplesPerBlock);
outBuffer.resize((size_t)samplesPerBlock);
// processBlock: ferry audio in and out through the network
auto* input = buffer.getReadPointer(channel);
std::copy(input, input + inBuffer.size(), inBuffer.begin());
processBlockNN(lstmModel, inBuffer, outBuffer, buffer.getNumSamples());
auto* output = buffer.getWritePointer(channel);
std::copy(outBuffer.begin(), outBuffer.begin() + inBuffer.size(), output);
```
- **What it demonstrates**: the complete audio→model→audio round-trip for a *trained*, script-exported model — structurally simpler than Ch.33's raw-LSTM version since state management moved inside the model itself.

## Anti-patterns
- Using `torch.jit.trace` for a model class with its own internal control-flow/state logic — use `torch.jit.script` instead, which analyzes the actual code rather than one recorded execution path.
- Loading a model file without checking it exists first — fails obscurely later instead of failing loudly and immediately.
- Trusting isolated microbenchmark numbers (Ch.32) as a guarantee of in-DAW real-time performance — actual DAW hosting overhead can be substantially worse; always test in the real target environment.

## Key Takeaways
1. `torch.jit.script` (not `.trace`) is required for models with their own internal control flow/state handling — this is the actual model class, not a bare `torch.nn.LSTM`.
2. Once state is internal to the model, the plugin's inference code simplifies back to Ch.32's state-less shape, just with a 3D (batched) input tensor instead of 2D.
3. Real DAW performance can be substantially worse than isolated benchmarks predicted — verify in the actual target host, not just a standalone timing script.
4. This performance gap (audible glitches even at moderate LSTM sizes, in a real DAW) is the direct motivation for the next chapter's RTNeural alternative.

## Connects To
- **Ch 33**: the plugin skeleton this chapter fills in with a real, trained model instead of a random one.
- **Ch 34-36**: the training pipeline that produces the `.pth` checkpoint this chapter exports and deploys.
- **Ch 38**: RTNeural, introduced specifically to solve the real-time performance shortfall demonstrated here.
