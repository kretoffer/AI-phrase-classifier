import numpy as np
import json
import yaml

from src.tokinizator import tokenize
from src.embedding import embedding

def classificate(project_path: str, message: str):

    with open(f"{project_path}/vocab.json") as f:
        vocab = json.load(f)

    model = np.load(f"{project_path}/classifier.npz")

    weights_input_to_hidden = model["weights_input_to_hidden"]
    weights_hidden_to_output = model["weights_hidden_to_output"]

    bias_input_to_hidden = model["bias_input_to_hidden"]
    bias_hidden_to_output = model["bias_hidden_to_output"]

    embedding_matrix = model["embedding_matrix"]


    tokens = tokenize(message, vocab)
    emb = embedding(embedding_matrix, tokens)

    input_neurons = np.reshape(emb, (-1, 1))

    hidden_raw = bias_input_to_hidden + weights_input_to_hidden @ input_neurons
    hidden = 1 / (1 + np.exp(-hidden_raw)) #sigmoid
    output_raw = bias_hidden_to_output + weights_hidden_to_output @ hidden

    output = list(1 / (1 + np.exp(-output_raw))) #sigmoid

    intent_index = output.index(max(output))
    with open(f"{project_path}/config.yaml") as f:
        project_data = yaml.load(f, Loader=yaml.SafeLoader)

    intent = project_data["intents"][intent_index]
    return intent