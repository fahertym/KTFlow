from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


def load_jsonl(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def main() -> None:
    st.title("KTFlow Labeler")
    input_path = st.text_input(
        "Seed JSONL", "data/interim/answer_keys/kt_control_v1_sentences.seed.jsonl"
    )
    out_path = st.text_input(
        "Output JSONL", "data/interim/answer_keys/kt_control_v1_sentences.jsonl"
    )
    labels = ["S", "L", "R", "St", "G", "M", "UNK"]

    if st.button("Load"):
        st.session_state.rows = load_jsonl(input_path)

    rows = st.session_state.get("rows", [])
    edited: list[dict] = []
    correct = 0
    total = 0
    for r in rows:
        text = r.get("text") or r.get("sentence")
        suggested = r.get("layer_suggested") or r.get("layer")
        final = st.selectbox(
            text, labels, index=labels.index(suggested) if suggested in labels else 0
        )
        edited.append({"text": text, "layer": final})
        total += 1
        if suggested == final:
            correct += 1

    if total > 0:
        st.write(f"Agreement with seed: {correct}/{total} ({100*correct/total:.1f}%)")

    if st.button("Save"):
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for r in edited:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        st.success(f"Saved {out_path}")


if __name__ == "__main__":
    main()
