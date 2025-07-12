import numpy as np


methods = {
    "sigmoid": lambda raw: (1 / (1 + np.exp(-raw)))
}

def activate(raw, method: str = "sigmoid"):
    return methods[method](raw) if method in methods else methods["sigmoid"](raw)