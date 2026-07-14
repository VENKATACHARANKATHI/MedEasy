"""
MedEasy — Multinomial Naive Bayes Classifier (built from scratch using NumPy)

Formula:
  log P(class | doc) = log P(class) + Σ [ x_i × log P(word_i | class) ]
  
  With Laplace smoothing (alpha = 0.5):
  P(word | class) = (count(word, class) + α) / (Σ counts + α × |vocab|)

Prediction:
  Returns class with highest log posterior
  Confidence via softmax over log posteriors
"""

import numpy as np


class MultinomialNaiveBayes:
    """
    Multinomial Naive Bayes from scratch.
    
    Args:
        alpha (float): Laplace smoothing parameter (default 0.5)
    
    Attributes:
        classes_ (list): List of class labels
        class_log_prior_ (np.ndarray): Log prior probability per class
        feature_log_prob_ (np.ndarray): Log P(word | class) matrix
    """

    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
        self.classes_ = []
        self.class_log_prior_ = None
        self.feature_log_prob_ = None
        self._fitted = False

    def fit(self, X: np.ndarray, y: list) -> "MultinomialNaiveBayes":
        """
        Train the classifier.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features) — TF-IDF vectors
            y: List of class labels of length n_samples
        Returns:
            self
        """
        self.classes_ = list(dict.fromkeys(y))  # preserve order, deduplicate
        n_classes = len(self.classes_)
        n_features = X.shape[1]
        n_samples = X.shape[0]

        # Log prior: log P(class) = log(count(class) / n_samples)
        class_counts = np.array([np.sum(np.array(y) == c) for c in self.classes_], dtype=float)
        self.class_log_prior_ = np.log(class_counts / n_samples)

        # Feature log probabilities with Laplace smoothing
        # P(word | class) = (sum of word's TF-IDF in class + alpha) / (total + alpha * n_features)
        self.feature_log_prob_ = np.zeros((n_classes, n_features))

        for i, cls in enumerate(self.classes_):
            mask = np.array(y) == cls
            X_cls = X[mask]
            word_counts = X_cls.sum(axis=0) + self.alpha
            self.feature_log_prob_[i] = np.log(word_counts / (word_counts.sum()))

        self._fitted = True
        return self

    def predict_log_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Compute log posterior for each class.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
        Returns:
            Log posterior matrix of shape (n_samples, n_classes)
        """
        if not self._fitted:
            raise RuntimeError("Classifier must be fitted before predict.")
        return X @ self.feature_log_prob_.T + self.class_log_prior_

    def predict(self, X: np.ndarray) -> list:
        """
        Predict class labels.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
        Returns:
            List of predicted class labels
        """
        log_proba = self.predict_log_proba(X)
        indices = np.argmax(log_proba, axis=1)
        return [self.classes_[i] for i in indices]

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Compute class probabilities using softmax over log posteriors.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
        Returns:
            Probability matrix of shape (n_samples, n_classes)
        """
        log_proba = self.predict_log_proba(X)
        # Numerically stable softmax
        log_proba -= log_proba.max(axis=1, keepdims=True)
        exp_proba = np.exp(log_proba)
        return exp_proba / exp_proba.sum(axis=1, keepdims=True)

    def predict_single(self, x: np.ndarray) -> tuple:
        """
        Predict class and confidence for a single sample.
        
        Args:
            x: Feature vector of shape (n_features,)
        Returns:
            (predicted_class, confidence_score)
        """
        x = x.reshape(1, -1)
        proba = self.predict_proba(x)[0]
        best_idx = np.argmax(proba)
        return self.classes_[best_idx], float(proba[best_idx])

    def score(self, X: np.ndarray, y: list) -> float:
        """Compute accuracy on given data."""
        preds = self.predict(X)
        return sum(p == t for p, t in zip(preds, y)) / len(y)
