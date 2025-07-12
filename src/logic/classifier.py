import numpy as np
import json
import yaml

from src.logic.embedding import embedding
from src.logic.neuron_activation import activate
from src.logic.tokinizator import tokenize

def classificate(project_path: str, message: str):

    with open(f"{project_path}/vocab.json") as f:
        vocab = json.load(f)

    model = np.load(f"{project_path}/classifier.npz")

    weights_input_to_hidden = model["weights_input_to_hidden"]
    weights_hidden_to_output = model["weights_hidden_to_output"]

    bias_input_to_hidden = model["bias_input_to_hidden"]
    bias_hidden_to_output = model["bias_hidden_to_output"]

    embedding_matrix = model["embedding_matrix"]

    with open(f"{project_path}/config.yaml") as f:
        project_data = yaml.load(f, Loader=yaml.SafeLoader)

    activate_method = project_data["activation_method"]

    tokens = tokenize(message, vocab)
    emb = embedding(embedding_matrix, tokens)

    input_neurons = np.reshape(emb, (-1, 1))

    hidden_raw = bias_input_to_hidden + weights_input_to_hidden @ input_neurons
    hidden = activate(hidden_raw, activate_method)
    output_raw = bias_hidden_to_output + weights_hidden_to_output @ hidden

    output = list(activate(output_raw, activate_method))

    intent_index = output.index(max(output))

    intent = project_data["intents"][intent_index]
    return intent