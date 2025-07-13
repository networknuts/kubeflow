#!/usr/bin/env python3
import argparse
import logging
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType

logging.basicConfig(level=logging.INFO)

def parse_args():
    p = argparse.ArgumentParser()
    # model & data
    p.add_argument("--model_name_or_path", type=str, default="distilgpt2")
    p.add_argument("--train_file", type=str, default="/data/train.jsonl")
    p.add_argument("--validation_file", type=str, default="/data/valid.jsonl")
    # hyperparams
    p.add_argument("--per_device_train_batch_size", type=int, default=1)
    p.add_argument("--learning_rate", type=float, default=1e-4)
    p.add_argument("--num_train_epochs", type=int, default=1)
    # LoRA config
    p.add_argument("--r", type=int, default=8)
    p.add_argument("--lora_alpha", type=int, default=32)
    p.add_argument("--lora_dropout", type=float, default=0.05)
    p.add_argument("--output_dir", type=str, default="./output")
    return p.parse_args()

def main():
    args = parse_args()

    # 1) Load model & tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name_or_path,
        cache_dir="/root/.cache/hf"
    )
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name_or_path,
        cache_dir="/root/.cache/hf",
        use_fast=True
    )

    # ── Ensure we have a padding token ──────────────────────────────────────
    if tokenizer.pad_token is None:
        # Option A: alias pad_token to eos_token
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.eos_token_id
    # ────────────────────────────────────────────────────────────────────────

    # 2) Apply LoRA
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=args.r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
    )
    model = get_peft_model(model, peft_config)

    # 3) Prepare dataset
    data_files = {"train": args.train_file, "validation": args.validation_file}
    ds = load_dataset("json", data_files=data_files)
    def tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=128
        )
    ds = ds.map(tokenize, batched=True, remove_columns=["text"])

    # 4) TrainingArguments & Trainer
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.per_device_train_batch_size,
        learning_rate=args.learning_rate,
        num_train_epochs=args.num_train_epochs,
        logging_strategy="epoch",
        evaluation_strategy="epoch",
        save_strategy="no",
        logging_steps=1,
        report_to=[],
    )
    def compute_metrics(eval_pred):
        # HuggingFace returns loss in eval_pred.metrics["eval_loss"]
        return {}

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["validation"],
        compute_metrics=compute_metrics,
    )

    # 5) Train & Evaluate
    trainer.train()
    metrics = trainer.evaluate()

    # 6) Print out eval_loss for Katib
    eval_loss = metrics.get("eval_loss", None)
    print(f"eval_loss: {eval_loss}")

if __name__ == "__main__":
    main()
