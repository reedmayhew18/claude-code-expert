---
name: training-infra
description: Set up production training infrastructure with distributed training, experiment tracking, checkpointing, and reproducibility. Use when the user says "multi-GPU", "distributed training", "W&B", "Weights and Biases", "MLflow", "DDP", "experiment tracking", "resume training", or "reproducible".
argument-hint: "[focus: distributed|logging|checkpointing|reproducibility|all]"
---

# Training Infrastructure

Production-grade training setup beyond the basic training loop.

## Process

### Step 1: Determine Scope
- Single GPU + better logging and checkpointing?
- Multi-GPU on one machine (DDP)?
- Multi-node distributed (FSDP / DeepSpeed)?

### Step 2: Reproducibility Baseline
```python
import torch, numpy as np, random
def set_seed(seed=42):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True  # slower but reproducible
    torch.backends.cudnn.benchmark = False
```
Save ALL hyperparameters to JSON alongside checkpoints. Future you will thank present you.

### Step 3: Robust Checkpointing
```python
def save_checkpoint(model, optimizer, scheduler, epoch, loss, path):
    import tempfile, os
    # Atomic write: save to temp, then rename (prevents corruption on crash)
    tmp = tempfile.NamedTemporaryFile(dir=os.path.dirname(path), delete=False)
    torch.save({
        'epoch': epoch, 'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'scheduler_state_dict': scheduler.state_dict(),
        'loss': loss,
    }, tmp.name)
    os.rename(tmp.name, path)
```
Keep last N checkpoints (delete oldest). Save on metric improvement AND every N epochs.

### Step 4: Experiment Tracking

**Weights & Biases (most popular):**
```python
import wandb
wandb.init(project="my-project", config=hyperparams)
wandb.watch(model, log="all")  # log gradients + parameters
# In training loop:
wandb.log({"train_loss": loss, "lr": scheduler.get_last_lr()[0]})
```

**MLflow:**
```python
import mlflow
mlflow.start_run()
mlflow.log_params(hyperparams)
# In loop: mlflow.log_metrics({"loss": loss}, step=step)
mlflow.pytorch.log_model(model, "model")
```

**TensorBoard:**
```python
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter("runs/experiment_1")
writer.add_scalar("Loss/train", loss, step)
writer.add_scalar("LR", lr, step)
# Launch: tensorboard --logdir=runs
```

### Step 5: Distributed Data Parallel (DDP)
```bash
# Launch with torchrun (modern, recommended)
torchrun --nproc_per_node=4 train.py
```
```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

dist.init_process_group("nccl")
local_rank = int(os.environ["LOCAL_RANK"])
model = model.to(local_rank)
model = DDP(model, device_ids=[local_rank])

# DataLoader must use DistributedSampler
sampler = torch.utils.data.DistributedSampler(dataset)
loader = DataLoader(dataset, sampler=sampler)

# Only save/log on rank 0
if local_rank == 0:
    save_checkpoint(...)
    wandb.log(...)
```

### Step 6: HuggingFace Accelerate (Simpler Multi-GPU)
```bash
accelerate config  # interactive setup
accelerate launch train.py
```
```python
from accelerate import Accelerator
accelerator = Accelerator(mixed_precision="bf16")
model, optimizer, loader = accelerator.prepare(model, optimizer, loader)
# Replace loss.backward() with:
accelerator.backward(loss)
```

### Step 7: Environment Validation
Before long training runs:
- `nvidia-smi` — confirm GPU count and VRAM
- Estimate steps/second from first 10 steps
- Calculate estimated total time
- Verify disk space for checkpoints
- Test checkpoint save/load cycle before committing to hours of training
