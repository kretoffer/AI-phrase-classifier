from typing import Literal
import numpy as np

def softmax(raw):
    e_raw = np.exp(raw - np.max(raw))
    return e_raw / e_raw.sum(axis=-1, keepdims=True)

methods = {
    "sigmoid": lambda raw: (1 / (1 + np.exp(-raw))),
    "relu": lambda raw: np.maximum(0, raw),
    "tanh": lambda raw: np.tanh(raw),
    "leaky relu": lambda raw: np.where(raw > 0, raw, 0.01 * raw),
    "softmax": softmax,
    "swish": lambda raw: raw * methods["sigmoid"](raw),
    "mish": lambda raw: raw * np.tanh(np.log1p(np.exp(raw)))
}

def activate(raw, method: Literal["sigmoid", "relu", "tanh", "leaky relu", "softmax", "swish", "mish"] = "relu"):
    return methods[method](raw) if method in methods else methods["sigmoid"](raw)