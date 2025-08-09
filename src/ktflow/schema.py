# ruff: noqa: E402
from __future__ import annotations

"""Typed data schemas for KTFlow using Pydantic v2 models."""


from pydantic import BaseModel, Field


class SentenceRecord(BaseModel):
    doc_id: str
    i: int
    text: str = Field(alias="sentence")
    layer: str | None = None
    layer_pred: str | None = None
    span: tuple[int, int] | None = None

    class Config:
        populate_by_name = True


class FlowEdge(BaseModel):
    doc_id: str
    src: str
    dst: str
    k: int = 1
    count: int
