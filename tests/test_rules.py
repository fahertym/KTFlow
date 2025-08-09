from __future__ import annotations

import pytest
from ktflow.tag.rules import tag_sentence_rules


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Assume the model is linear.", "M"),
        ("In general, this principle applies to fluids.", "G"),
        ("Overall, the system works via feedback loops.", "St"),
        ("If pressure increases then volume decreases.", "R"),
        ("A photon is a quantum of electromagnetic radiation.", "L"),
        ("Terms: mass, energy, momentum.", "S"),
        ("This is unclear.", "UNK"),
    ],
)
def test_tag_sentence_rules(text: str, expected: str) -> None:
    assert tag_sentence_rules(text) == expected
