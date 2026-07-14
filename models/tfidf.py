"""
MedEasy — TF-IDF Vectorizer (built from scratch using NumPy only)

Formula:
  TF(t, d)  = count(t in d) / len(d)
  IDF(t)    = log((1 + N) / (1 + df(t))) + 1     [smoothed]
  TF-IDF    = TF * IDF

Cosine Similarity:
  sim(A, B) = A·B / (||A|| * ||B||)
"""

import re
import math
import numpy as np
from collections import Counter


STOPWORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "of", "and",
    "or", "not", "for", "this", "that", "are", "was", "be", "with", "by",
    "from", "as", "i", "you", "my", "what", "how", "when", "where", "which",
    "who", "me", "we", "our", "your", "his", "her", "its", "they", "them",
}


def tokenize(text: str) -> list:
    """Lowercase, remove punctuation, split, filter stopwords."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()
    return [t for t in tokens if len(t) > 1 and t not in STOPWORDS]


class TFIDFVectorizer:
    """
    Custom TF-IDF Vectorizer built with NumPy.
    
    Attributes:
        vocab (list): Sorted vocabulary list
        vocab_index (dict): Word → column index mapping
        idf (np.ndarray): IDF scores for each vocabulary word
        max_features (int): Maximum vocabulary size
    """

    def __init__(self, max_features: int = 500):
        self.max_features = max_features
        self.vocab = []
        self.vocab_index = {}
        self.idf = None
        self._fitted = False

    def fit(self, documents: list) -> "TFIDFVectorizer":
        """
        Build vocabulary and IDF from a list of text documents.
        
        Args:
            documents: List of raw text strings
        Returns:
            self (for chaining)
        """
        N = len(documents)
        
        # Count document frequency (df) for each term
        df = Counter()
        tokenized = []
        for doc in documents:
            tokens = set(tokenize(doc))
            tokenized.append(tokens)
            df.update(tokens)

        # Select top max_features by document frequency
        top_words = [w for w, _ in df.most_common(self.max_features)]
        self.vocab = sorted(top_words)
        self.vocab_index = {w: i for i, w in enumerate(self.vocab)}

        # Compute IDF: log((1 + N) / (1 + df(t))) + 1
        self.idf = np.zeros(len(self.vocab))
        for i, word in enumerate(self.vocab):
            self.idf[i] = math.log((1 + N) / (1 + df.get(word, 0))) + 1

        self._fitted = True
        return self

    def transform(self, documents: list) -> np.ndarray:
        """
        Convert documents to TF-IDF matrix.
        
        Args:
            documents: List of raw text strings
        Returns:
            np.ndarray of shape (n_docs, vocab_size)
        """
        if not self._fitted:
            raise RuntimeError("Vectorizer must be fitted before transform.")

        matrix = np.zeros((len(documents), len(self.vocab)))

        for i, doc in enumerate(documents):
            tokens = tokenize(doc)
            if not tokens:
                continue
            tf = Counter(tokens)
            doc_len = len(tokens)
            for word, count in tf.items():
                if word in self.vocab_index:
                    j = self.vocab_index[word]
                    matrix[i, j] = (count / doc_len) * self.idf[j]

        return matrix

    def fit_transform(self, documents: list) -> np.ndarray:
        """Fit and transform in one step."""
        self.fit(documents)
        return self.transform(documents)

    def transform_single(self, text: str) -> np.ndarray:
        """
        Transform a single text string to a TF-IDF vector.
        
        Args:
            text: Raw text string
        Returns:
            np.ndarray of shape (vocab_size,)
        """
        return self.transform([text])[0]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    sim(A, B) = A·B / (||A|| * ||B||)
    Returns value in [0.0, 1.0]
    """
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def cosine_similarity_matrix(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between a query vector and all rows of a matrix.
    
    Args:
        query: 1D array of shape (vocab_size,)
        matrix: 2D array of shape (n_docs, vocab_size)
    Returns:
        1D array of similarities of shape (n_docs,)
    """
    norm_q = np.linalg.norm(query)
    if norm_q == 0:
        return np.zeros(matrix.shape[0])
    norms = np.linalg.norm(matrix, axis=1)
    norms[norms == 0] = 1e-10  # avoid division by zero
    dots = matrix @ query
    return dots / (norms * norm_q)
