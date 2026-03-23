---
name: torch-optimize
description: Profile and optimize PyTorch training and inference for speed and memory. Use when the user says "too slow", "OOM", "out of memory", "optimize training", "speed up", "torch profiler", "mixed precision", "memory efficient", "faster", or "GPU utilization".
argument-hint: "[problem: speed|memory|both]"
---

# PyTorch Optimization

Diagnose and fix performance and memory issues in PyTorch code.

## Process

### Step 1: Identify the Bottleneck
Ask: is the problem training speed, inference speed, or GPU OOM?
Check GPU utilization first:
```bash
nvidia-smi  # or watch -n1 nvidia-smi
# Low GPU util (< 80%) = DataLoader bottleneck, not compute
# High GPU util + slow = compute-bound, need algorithmic changes
# OOM = memory-bound, need reduction techniques
```

### Step 2: Profile
```python
with torch.profiler.profile(
    activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True
) as prof:
    # Run a few training steps
    ...
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=20))
```
Identify: CPU-GPU transfer bottleneck vs compute bottleneck vs memory bottleneck.

### Step 3: Mixed Precision
```python
# Ampere+ GPUs: use bfloat16 (no scaler needed)
with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
    output = model(input)

# Older GPUs: use float16 + GradScaler
scaler = torch.GradScaler()
```
If loss goes NaN with fp16: scale factor too high, or you have ops that need fp32 (softmax, layer norm typically handled automatically).

### Step 4: Memory Reduction
In order of effort (try top first):
1. **Reduce batch size** + increase `gradient_accumulation_steps` to compensate
2. **`torch.autocast`** — halves activation memory
3. **Gradient checkpointing**: `torch.utils.checkpoint.checkpoint()` — trades compute for memory (~30% slower, ~60% less memory)
4. **`del` intermediate tensors** + `torch.cuda.empty_cache()` between phases
5. **`torch.backends.cudnn.benchmark = True`** — autotuner picks fastest convolution algorithm

### Step 5: DataLoader Tuning
```python
DataLoader(
    dataset,
    num_workers=os.cpu_count(),  # match CPU cores
    pin_memory=True,             # CUDA only
    persistent_workers=True,     # avoid respawning workers
    prefetch_factor=2,           # pre-load next batches
)
```

### Step 6: torch.compile
```python
model = torch.compile(model, mode='reduce-overhead')  # default good
# mode='max-autotune' for best throughput (slow first run)
```
Requirements: PyTorch 2.0+, model with no dynamic control flow, stable input shapes. Check compatibility before assuming it works.

### Step 7: Inference Optimization
- `model.eval()` + `torch.no_grad()` (always)
- Batch inference (don't process one sample at a time)
- TorchScript for deployment: `torch.jit.trace(model, example_input)`
- Dynamic quantization for int8: `torch.quantization.quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)`

## Anti-Patterns
- Calling `.item()`, `.numpy()`, or `.cpu()` inside training loops (GPU sync stall)
- Moving tensors between devices repeatedly in a loop
- Using `.cuda()` instead of `.to(device)` (not device-agnostic)
- Optimizing without profiling first (guessing the bottleneck is usually wrong)
