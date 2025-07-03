import numpy as np
from typing import List


def generate_matrix(vocab_size: int, embedding_dim: int = 32):
    return np.random.randn(vocab_size, embedding_dim) * 0.01

def embedding(embedding_matrix, sequence: List[int]):
    return np.array([embedding_matrix[idx] for idx in sequence])