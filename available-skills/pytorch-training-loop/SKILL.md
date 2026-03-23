---
name: pytorch-training-loop
description: Build a complete PyTorch training loop with best practices. Use when the user says "training loop", "train a model", "PyTorch training", "write the training code", "fit a model", or "set up training".
argument-hint: "[model type] [task: classification|regression|generation|custom]"
disable-model-invocation: true
---

# PyTorch Training Loop

Build a production-quality training loop from scratch with proper structure.

## Process

### Step 1: Clarify Requirements
- Device: CPU, CUDA, MPS (Apple Silicon)?
- Mixed precision needed? (yes if CUDA with Ampere+ GPU)
- Gradient accumulation? (yes if batch size limited by VRAM)
- Checkpointing strategy?

### Step 2: Dataset & DataLoader
```python
# Subclass torch.utils.data.Dataset
# DataLoader with:
#   num_workers = os.cpu_count()
#   pin_memory = True (CUDA only)
#   collate_fn for variable-length inputs
#   drop_last = True for training (stable batch norm)
```
Use a proper train/val split. Never evaluate on training data.

### Step 3: Model Initialization
- `model.to(device)` after construction
- Consider `torch.compile(model)` for PyTorch 2.0+ (stable models, repeated forward passes)
- Log parameter count: `sum(p.numel() for p in model.parameters() if p.requires_grad)`

### Step 4: Optimizer & Scheduler
- **AdamW** for most tasks. `weight_decay` only on non-bias, non-LayerNorm params.
- **SGD + momentum** for CNNs when tuning for absolute best accuracy.
- LR scheduler: cosine annealing (default good), OneCycleLR (fast convergence), linear warmup + decay (LLMs).
- `GradScaler` if using mixed precision.

### Step 5: Training Loop
```python
model.train()
for batch in train_loader:
    optimizer.zero_grad(set_to_none=True)  # faster than zero_grad()
    with torch.autocast(device_type='cuda', dtype=torch.float16):  # mixed precision
        output = model(batch)
        loss = criterion(output, targets)
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    scaler.step(optimizer)
    scaler.update()
    scheduler.step()  # if per-step scheduler
```

### Step 6: Validation Loop
```python
model.eval()
with torch.no_grad():
    # Accumulate metrics as scalars, NOT tensors
    total_loss = 0.0  # float, not tensor
    for batch in val_loader:
        ...
        total_loss += loss.item()  # .item() OK here (outside training)
```

### Step 7: Checkpointing
Save model state, optimizer state, scheduler state, epoch, and best metric. Use atomic writes (save to temp, then rename). Keep last N checkpoints.

### Step 8: Logging
Choose one: TensorBoard (`SummaryWriter`), W&B (`wandb.log`), or structured JSON. Log loss, learning rate, gradient norms, and validation metrics per epoch.

## Anti-Patterns
- **Never** call `.item()` inside the training loop (forces GPU sync)
- **Never** accumulate tensors for metrics (memory leak) — use `float` accumulators
- **Never** forget `model.train()` / `model.eval()` switching
- **Never** use `optimizer.zero_grad()` without `set_to_none=True` (wastes memory)
- **Never** skip gradient clipping without good reason (exploding gradients are silent until NaN)
