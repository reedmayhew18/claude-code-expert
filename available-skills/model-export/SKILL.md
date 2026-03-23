---
name: model-export
description: Export and quantize ML models for deployment. Use when the user says "export model", "GGUF", "llama.cpp", "quantize", "ONNX", "TorchScript", "deploy model", "convert model", "run locally", "Ollama", or "inference server".
argument-hint: "[source format] [target: gguf|onnx|torchscript|int8]"
---

# Model Export & Quantization

Convert trained models into deployment-ready formats.

## Process

### Step 1: Identify Source and Target
- **Source**: HuggingFace safetensors, PyTorch .pt/.pth, Unsloth output?
- **Target**: Where will it run?

| Deployment Target | Format | Tool |
|---|---|---|
| llama.cpp / Ollama / local | GGUF | llama.cpp convert scripts |
| ONNX Runtime / edge / web | ONNX | `torch.onnx.export` or Optimum |
| C++ / mobile / embedded | TorchScript | `torch.jit.trace` / `torch.jit.script` |
| Same PyTorch but faster | int8 quantized | `torch.quantization` |
| vLLM / TGI server | HF safetensors | Already correct format |

### Step 2: GGUF (for llama.cpp / Ollama)
```bash
# Clone llama.cpp
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp

# Convert HuggingFace model to GGUF
python convert_hf_to_gguf.py /path/to/hf-model --outfile model.gguf --outtype f16

# Quantize
./llama-quantize model.gguf model-q4_k_m.gguf q4_k_m
```

**Quantization types** (from largest/best to smallest/fastest):
| Type | Size vs f16 | Quality | Use when |
|------|------------|---------|----------|
| f16 | 100% | Lossless | Unlimited VRAM/disk |
| q8_0 | ~50% | Near-lossless | Good hardware, want quality |
| q5_k_m | ~35% | Very good | Balanced |
| **q4_k_m** | **~25%** | **Good** | **Recommended default** |
| q3_k_m | ~20% | Acceptable | Limited resources |
| q2_k | ~15% | Noticeable loss | Extreme constraints |

Test with: `./llama-cli -m model-q4_k_m.gguf -p "Test prompt" -n 100`

### Step 3: ONNX Export
```python
# PyTorch model
import torch
dummy_input = torch.randn(1, 3, 224, 224)  # match your input shape
torch.onnx.export(model, dummy_input, "model.onnx",
    input_names=["input"], output_names=["output"],
    dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}})

# HuggingFace transformer (use Optimum)
# pip install optimum[exporters]
# optimum-cli export onnx --model model_name ./onnx_output/
```
Verify: `onnxruntime.InferenceSession("model.onnx").run(None, {"input": data})`

### Step 4: TorchScript
```python
# Trace (works for most models, no control flow)
traced = torch.jit.trace(model, example_input)
traced.save("model_traced.pt")

# Script (supports control flow, stricter)
scripted = torch.jit.script(model)
scripted.save("model_scripted.pt")
```
Load anywhere: `model = torch.jit.load("model_traced.pt")`

### Step 5: PyTorch int8 Quantization
```python
# Dynamic quantization (easiest, good for Linear/LSTM layers)
quantized = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# Static quantization (better quality, needs calibration data)
# Requires: prepare -> calibrate -> convert workflow
```

### Step 6: Verify Export
For ANY export path:
1. Run inference with both original and exported model on same inputs
2. Compare outputs (should be close, not necessarily identical for quantized)
3. Benchmark speed improvement
4. Check output file size matches expectations
