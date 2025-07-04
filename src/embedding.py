import numpy as np
from typing import List


def generate_matrix(vocab_size: int, embedding_dim: int = 32):
    matrix = np.random.randn(vocab_size+1, embedding_dim) * 0.01
    matrix[0] = np.zeros(embedding_dim)
    return matrix

def embedding(embedding_matrix, sequence: List[int]):
    return np.array([embedding_matrix[idx] for idx in sequence])