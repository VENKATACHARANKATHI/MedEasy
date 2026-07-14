"""
MedEasy — Report Type Classifier

Trains TF-IDF + Naive Bayes on startup (<1 second).
Classifies medical reports into 10 categories.
"""

import numpy as np
from .tfidf import TFIDFVectorizer
from .naive_bayes import MultinomialNaiveBayes
from data.training_data import REPORT_TRAINING, REPORT_TYPES
import random


class ReportTypeClassifier:
    """
    Classifies medical reports using TF-IDF + Multinomial Naive Bayes.
    
    Trained on 74 labeled samples across 10 report categories.
    Training happens on first instantiation (< 1 second).
    """

    def __init__(self):
        self.vectorizer = TFIDFVectorizer(max_features=600)
        self.model = MultinomialNaiveBayes(alpha=0.5)
        self._trained = False
        self.accuracy = 0.0
        self._train()

    def _augment(self, texts: list, labels: list, factor: int = 2) -> tuple:
        """
        Simple data augmentation: shuffle words in each sample.
        Doubles training data without adding new information.
        """
        aug_texts, aug_labels = list(texts), list(labels)
        for text, label in zip(texts, labels):
            words = text.split()
            for _ in range(factor - 1):
                random.shuffle(words)
                aug_texts.append(" ".join(words))
                aug_labels.append(label)
        return aug_texts, aug_labels

    def _train(self):
        """Train on REPORT_TRAINING samples with augmentation."""
        texts  = [t for t, _ in REPORT_TRAINING]
        labels = [l for _, l in REPORT_TRAINING]

        # Augment: 74 → ~148 samples
        texts, labels = self._augment(texts, labels, factor=2)

        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)

        self.accuracy = self.model.score(X, labels)
        self._trained = True
        print(f"[Classifier] Trained on {len(texts)} samples, {len(set(labels))} classes | accuracy={self.accuracy:.2%}")

    def predict(self, text: str) -> dict:
        """
        Predict report type from text.
        
        Args:
            text: Raw report text string
        Returns:
            dict with keys: type, confidence, all_scores
        """
        if not self._trained:
            return {"type": "General Medical Report", "confidence": 0.5}

        # Keyword-based pre-check with primary keyword boosting (2x weight)
        text_lower = text.lower()
        best_type, best_score = None, 0
        for rtype in REPORT_TYPES:
            base_hits = sum(1 for k in rtype["keys"] if k in text_lower)
            primary_hits = sum(1 for k in rtype.get("primary", []) if k in text_lower)
            total_score = base_hits + (primary_hits * 2)
            if total_score > best_score:
                best_score = total_score
                best_type = rtype
        if best_type and best_score >= 3:
            return {
                "type": best_type["name"],
                "confidence": min(0.99, max(0.55, best_score / 9)),
                "source": "keyword",
            }

        # ML prediction
        x = self.vectorizer.transform_single(text[:1200])  # truncate to first 1200 chars
        predicted_class, confidence = self.model.predict_single(x)

        # Map short class name to full name
        full_name = next(
            (r["name"] for r in REPORT_TYPES if r["name"].startswith(predicted_class)),
            predicted_class
        )

        return {
            "type": full_name,
            "confidence": round(confidence, 3),
            "source": "ml",
        }
