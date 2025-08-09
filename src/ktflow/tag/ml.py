from __future__ import annotations

"""Machine-learning tagger based on TF-IDF + Logistic Regression."""

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder


@dataclass
class ModelBundle:
    vectorizer: TfidfVectorizer
    classifier: LogisticRegression
    label_encoder: LabelEncoder


def featurize(
    sentences: Iterable[str],
    vectorizer: Optional[TfidfVectorizer] = None,
) -> Tuple[TfidfVectorizer, np.ndarray]:
    """Fit or transform sentences into TF-IDF features.

    Uses a mixed char + word n-gram representation for robustness on short texts.
    """
    if vectorizer is None:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
        )
    X = vectorizer.fit_transform(list(sentences)) if not hasattr(vectorizer, "vocabulary_") else vectorizer.transform(list(sentences))
    return vectorizer, X


def train_tfidf_lr(train_jsonl: str, label_col: str = "layer", text_col: str = "text") -> ModelBundle:
    """Train a TF-IDF + LogisticRegression classifier on a JSONL dataset.

    Parameters
    ----------
    train_jsonl: str
        Path to JSONL with fields including ``text`` and label_col.
    label_col: str
        Column name for labels (default: ``layer``).
    text_col: str
        Column name for sentence text (default: ``text``).
    """
    import json

    texts: List[str] = []
    labels: List[str] = []
    with open(train_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            texts.append(row[text_col])
            labels.append(row[label_col])

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)

    # Use hybrid char word TF-IDF by stacking two vectorizers
    # Simpler: use a single char_wb vectorizer; empirically robust for short sents
    vectorizer = TfidfVectorizer(lowercase=True, analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    X = vectorizer.fit_transform(texts)

    clf = LogisticRegression(max_iter=1000, random_state=42, n_jobs=None, multi_class="auto")
    clf.fit(X, y)

    return ModelBundle(vectorizer=vectorizer, classifier=clf, label_encoder=label_encoder)


def predict(model: ModelBundle, sentences: List[str]) -> List[str]:
    """Predict labels using the trained model."""
    X = model.vectorizer.transform(sentences)
    y = model.classifier.predict(X)
    labels = model.label_encoder.inverse_transform(y)
    return list(labels)


def predict_proba(model: ModelBundle, sentences: List[str]) -> np.ndarray:
    """Return class probabilities (n_samples x n_classes)."""
    X = model.vectorizer.transform(sentences)
    return model.classifier.predict_proba(X)


