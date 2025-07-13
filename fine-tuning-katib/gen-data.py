#!/usr/bin/env python3
import argparse
import json
from datasets import load_dataset

def main():
    parser = argparse.ArgumentParser(
        description="Load Wikitext-2 raw and split into JSONL train/valid for Katib"
    )
    parser.add_argument(
        "--config_name",
        type=str,
        default="wikitext-2-raw-v1",
        help="Hugging Face Wikitext config (e.g. 'wikitext-2-raw-v1')"
    )
    parser.add_argument(
        "--split_ratio",
        type=float,
        default=0.8,
        help="Fraction of the original train split to keep as training set"
    )
    parser.add_argument(
        "--train_jsonl",
        type=str,
        default="train.jsonl",
        help="Output path for training JSONL"
    )
    parser.add_argument(
        "--valid_jsonl",
        type=str,
        default="valid.jsonl",
        help="Output path for validation JSONL"
    )
    args = parser.parse_args()

    # 1) Load only the 'train' split of Wikitext
    ds = load_dataset("wikitext", args.config_name, split="train")

    # 2) Do an 80/20 split on that train split
    split = ds.train_test_split(test_size=1 - args.split_ratio, seed=42)
    train_ds, valid_ds = split["train"], split["test"]

    # 3) Write out JSONL
    def write_jsonl(dset, path):
        with open(path, "w") as f:
            for ex in dset:
                text = ex["text"].strip()
                if not text:
                    continue
                f.write(json.dumps({"text": text}) + "\n")

    write_jsonl(train_ds, args.train_jsonl)
    write_jsonl(valid_ds, args.valid_jsonl)

    print(f"✅ Wrote {len(train_ds)} records to {args.train_jsonl}")
    print(f"✅ Wrote {len(valid_ds)} records to {args.valid_jsonl}")

if __name__ == "__main__":
    main()
