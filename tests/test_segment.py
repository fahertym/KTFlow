from __future__ import annotations

from ktflow.segment.sentence import split_sentences


def test_split_sentences_basic() -> None:
    text = (
        "Photosynthesis converts light to energy. It occurs in chloroplasts! "
        "Does it require water? Yes."
    )
    sents = split_sentences(text)
    assert sents == [
        "Photosynthesis converts light to energy.",
        "It occurs in chloroplasts!",
        "Does it require water?",
        "Yes.",
    ]


def test_split_sentences_whitespace() -> None:
    text = "A.  B\nC \n D."
    sents = split_sentences(text)
    assert sents == ["A.", "B C D."]
