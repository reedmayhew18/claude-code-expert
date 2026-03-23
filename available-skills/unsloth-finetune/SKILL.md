---
name: unsloth-finetune
description: Fine-tune LLMs with Unsloth for 2x+ faster training and lower memory usage. Use when the user says "Unsloth", "unsloth", "fast fine-tuning", "efficient LoRA", or wants to fine-tune Llama, Mistral, Qwen, or Gemma efficiently.
argument-hint: "[base model name] [dataset path or format]"
---

# Unsloth Fine-Tuning

Fast LLM fine-tuning with Unsloth's optimized API. 2x+ speed, 60%+ less memory vs vanilla HuggingFace.

## Process

### Step 1: Environment Setup
```bash
pip install unsloth
# Verify CUDA compatibility
python -c "import unsloth; print('Unsloth ready')"
```
Supported models: Llama 3.x, Mistral, Qwen 2.5, Gemma 2, Phi-3/4, and more. Check Unsloth docs for current list.

### Step 2: Load Model
```python
from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.1-8B-bnb-4bit",  # or any supported model
    max_seq_length=2048,
    dtype=None,          # auto-detect (bf16 on Ampere+, fp16 otherwise)
    load_in_4bit=True,   # 4-bit quantization for memory efficiency
)
```

### Step 3: Apply LoRA
```python
model = FastLanguageModel.get_peft_model(
    model,
    r=16,                # rank: 16 for most tasks, 32 for complex
    lora_alpha=16,
    lora_dropout=0,      # Unsloth optimized: 0 is fine
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    use_gradient_checkpointing="unsloth",  # Unsloth's optimized checkpointing
)
```

### Step 4: Prepare Dataset
```python
# Format with chat template
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(tokenizer, chat_template="llama-3.1")

# For instruction tuning: use train_on_responses_only
from trl import SFTTrainer
from unsloth import is_bfloat16_supported

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    max_seq_length=2048,
    dataset_num_proc=2,
)
# IMPORTANT: train on responses only (don't learn to repeat instructions)
trainer = train_on_responses_only(trainer, tokenizer)
```

### Step 5: Train
```python
from transformers import TrainingArguments
args = TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_steps=5,
    num_train_epochs=1,
    learning_rate=2e-4,
    fp16=not is_bfloat16_supported(),
    bf16=is_bfloat16_supported(),
    logging_steps=1,
    output_dir="outputs",
)
trainer.train()
```

### Step 6: Export
```python
# Save LoRA adapter only
model.save_pretrained_merged("output", tokenizer, save_method="lora")

# Merge to full 16-bit model
model.save_pretrained_merged("output-16bit", tokenizer, save_method="merged_16bit")

# Export to GGUF for llama.cpp / Ollama
model.save_pretrained_gguf("output-gguf", tokenizer, quantization_method="q4_k_m")
# Options: q8_0 (near-lossless), q4_k_m (recommended), q3_k_m (small), f16 (full)
```

### Step 7: Test Exported Model
```bash
# With Ollama
ollama create mymodel -f output-gguf/Modelfile
ollama run mymodel "Your test prompt"

# With llama.cpp
./llama-cli -m output-gguf/model-q4_k_m.gguf -p "Your test prompt"
```
Verify the output matches the chat template used during training.

## Anti-Patterns
- **Wrong chat template**: If training used llama-3.1 template but inference uses a different one, instruction following breaks
- **Not using `train_on_responses_only`**: Model learns to repeat instructions instead of just answering
- **GGUF quant mismatch**: q4_k_m is the sweet spot. q2_k loses too much quality for most tasks
- **Skipping the test**: Always run inference on the exported model before declaring success
