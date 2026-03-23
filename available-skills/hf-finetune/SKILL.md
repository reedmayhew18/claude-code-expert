---
name: hf-finetune
description: Fine-tune a HuggingFace transformer model with Trainer API or custom loop. Use when the user says "fine-tune", "finetune", "HuggingFace", "Trainer", "SFT", "PEFT", "LoRA", "custom LLM", "adapt a model", or "train a transformer".
argument-hint: "[base model] [task: classification|seq2seq|causal-lm|token-classification]"
---

# HuggingFace Fine-Tuning

Fine-tune transformer models using the HuggingFace ecosystem.

## Process

### Step 1: Clarify the Task
- Base model name (e.g., `meta-llama/Llama-3.1-8B`, `mistralai/Mistral-7B-v0.3`)
- Task type: causal LM, classification, seq2seq, token classification
- Dataset format: what columns, what structure
- Hardware: GPU VRAM determines approach (>24GB = full fine-tune possible, <24GB = LoRA)

### Step 2: Dataset Preparation
```python
from datasets import load_dataset
dataset = load_dataset("path_or_name")

# Tokenize
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token  # common fix for causal LMs
tokenizer.padding_side = "left"  # REQUIRED for batched causal LM inference

def tokenize(examples):
    return tokenizer(examples["text"], truncation=True, max_length=2048)

dataset = dataset.map(tokenize, batched=True)
```
**Always** print 2-3 tokenized examples to verify formatting before training.

### Step 3: LoRA Decision
| VRAM | Approach |
|------|----------|
| >40GB | Full fine-tune |
| 16-40GB | LoRA (r=16, alpha=32) |
| <16GB | QLoRA (4-bit base + LoRA) |

```python
from peft import LoraConfig, get_peft_model
config = LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],  # attention layers
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, config)
model.print_trainable_parameters()  # should be ~1-5% of total
```

### Step 4: Model Loading
```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,     # NEVER leave as default fp32
    device_map="auto",               # auto-shard across GPUs
    attn_implementation="flash_attention_2",  # if available
    # For QLoRA:
    # quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
)
```

### Step 5: TrainingArguments
```python
TrainingArguments(
    output_dir="./output",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,   # effective batch = 16
    learning_rate=2e-4,              # LoRA typical; full fine-tune: 2e-5
    num_train_epochs=3,
    warmup_ratio=0.1,
    lr_scheduler_type="cosine",
    bf16=True,
    save_strategy="epoch",
    evaluation_strategy="epoch",
    logging_steps=10,
)
```

### Step 6: Train
```python
from trl import SFTTrainer  # for instruction tuning
trainer = SFTTrainer(model=model, args=args, train_dataset=train, eval_dataset=val)
trainer.train()
```

### Step 7: Save & Merge
```python
# LoRA: merge weights before saving for deployment
model = model.merge_and_unload()
model.save_pretrained("./merged-model")
tokenizer.save_pretrained("./merged-model")
```

### Step 8: Verify
Reload the saved model, run inference, compare to base model output. Confirm the model follows the fine-tuned behavior.

## Common Issues
- **Wrong chat template**: Ruins instruction following. Always use `tokenizer.apply_chat_template()`.
- **Padding side**: Causal LMs MUST use left-padding for batched inference.
- **dtype default**: Loading without `torch_dtype` defaults to fp32 and OOMs.
- **Tokenizer mismatch**: Save tokenizer alongside model. Always reload both from the same directory.
