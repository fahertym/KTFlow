# ruff: noqa: E402, PLR0913
from __future__ import annotations

"""Hugging Face transformer-based tagger (sequence classification)."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)


@dataclass
class HFModelBundle:
    model_dir: Path


def _read_jsonl(path: str) -> list[dict]:
    rows: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _prepare_dataset(rows: list[dict], label_col: str) -> tuple[list[str], list[str]]:
    texts = [r["text"] for r in rows]
    labels = [r[label_col] for r in rows]
    return texts, labels


def train_hf_classifier(
    train_jsonl: str,
    model_name: str,
    out_dir: str,
    label_col: str = "layer",
    epochs: int = 3,
    batch_size: int = 32,
    lr: float = 2e-5,
    fp16: bool = True,
) -> HFModelBundle:
    rows = _read_jsonl(train_jsonl)
    texts, labels = _prepare_dataset(rows, label_col)

    unique_labels = sorted(set(labels))
    label2id = {lab: i for i, lab in enumerate(unique_labels)}
    id2label = {i: lab for lab, i in label2id.items()}
    y = [label2id[lab] for lab in labels]

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    class Dataset:
        def __init__(self, texts: list[str], y: list[int]):
            self.texts = texts
            self.y = y

        def __len__(self) -> int:
            return len(self.texts)

        def __getitem__(self, idx: int) -> dict:
            enc = tokenizer(self.texts[idx], truncation=True, padding="max_length", max_length=256)
            enc["labels"] = self.y[idx]
            return enc

    dataset = Dataset(texts, y)

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=len(unique_labels), id2label=id2label, label2id=label2id
    )

    training_args = TrainingArguments(
        output_dir=out_dir,
        per_device_train_batch_size=batch_size,
        learning_rate=lr,
        num_train_epochs=epochs,
        fp16=fp16,
        logging_steps=50,
        save_strategy="epoch",
        report_to=[],
    )

    trainer = Trainer(model=model, args=training_args, train_dataset=dataset)
    trainer.train()

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    with open(Path(out_dir) / "labels.json", "w", encoding="utf-8") as f:
        json.dump({"label2id": label2id, "id2label": id2label}, f, ensure_ascii=False)

    return HFModelBundle(model_dir=Path(out_dir))


def _load_hf(model_dir: str) -> tuple[Any, Any, dict[int, str]]:
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    with open(Path(model_dir) / "labels.json", encoding="utf-8") as f:
        m = json.load(f)
    id2label = {int(k): v for k, v in m["id2label"].items()}
    return model, tokenizer, id2label


def predict_hf(model_dir: str, sentences: list[str]) -> list[str]:
    model, tokenizer, id2label = _load_hf(model_dir)
    model.eval()
    preds: list[str] = []
    for s in sentences:
        enc = tokenizer(s, return_tensors="pt", truncation=True, padding=True, max_length=256)
        logits = model(**{k: v for k, v in enc.items()}).logits.detach().cpu().numpy()[0]
        label = id2label[int(np.argmax(logits))]
        preds.append(label)
    return preds


def predict_proba_hf(model_dir: str, sentences: list[str]) -> tuple[np.ndarray, list[str]]:
    model, tokenizer, id2label = _load_hf(model_dir)
    model.eval()
    labels = [id2label[i] for i in sorted(id2label.keys())]
    probs_list: list[np.ndarray] = []
    for s in sentences:
        enc = tokenizer(s, return_tensors="pt", truncation=True, padding=True, max_length=256)
        logits = model(**{k: v for k, v in enc.items()}).logits.detach().cpu().numpy()[0]
        e_x = np.exp(logits - np.max(logits))
        probs = e_x / e_x.sum()
        probs_list.append(probs)
    return np.vstack(probs_list), labels
