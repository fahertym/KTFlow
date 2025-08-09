from __future__ import annotations

from ktflow.schema import FlowEdge, SentenceRecord


def test_sentence_record_alias() -> None:
    rec = SentenceRecord(doc_id="d", i=0, sentence="Hello.")
    assert rec.text == "Hello."
    assert rec.layer is None


def test_flow_edge_model() -> None:
    edge = FlowEdge(doc_id="d", src="S", dst="L", k=2, count=3)
    assert edge.k == 2  # noqa: PLR2004
    assert edge.count == 3  # noqa: PLR2004
