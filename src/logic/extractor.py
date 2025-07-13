import os
import pickle

import numpy as np
import yaml
from src.logic.neuron_activation import activate
from src.shemes import Project


def extract(project_path: str, emb_phrase, intent: str):
    entities = [f.replace(".pkl", "") for f in os.listdir(f"{project_path}/models/{intent}") if f.endswith(".pkl")]
    

    slots = []
    for entity in entities:
        slots.append({entity: extract_entity(project_path, emb_phrase, intent, entity)})
    
    return slots

def extract_entity(project_path: str, emb_phrase, intent: str, entity: str):
    with open(f"{project_path}/models/{intent}/{entity}.pkl", "rb") as f:
        values = pickle.load(f)

    model = np.load(f"{project_path}/models/{intent}/{entity}.npz")

    weights_input_to_hidden = model["weights_input_to_hidden"]
    weights_hidden_to_output = model["weights_hidden_to_output"]

    bias_input_to_hidden = model["bias_input_to_hidden"]
    bias_hidden_to_output = model["bias_hidden_to_output"]

    project = Project.model_validate(yaml.load(open(f"{project_path}/config.yaml", "r"), Loader=yaml.SafeLoader))

    input_neurons = np.reshape(emb_phrase, (-1, 1))

    hidden_raw = bias_input_to_hidden + weights_input_to_hidden @ input_neurons
    hidden = activate(hidden_raw, project.activation_method)
    output_raw = bias_hidden_to_output + weights_hidden_to_output @ hidden

    output = list(activate(output_raw, project.activation_method))

    entity_index = output.index(max(output))

    return values[entity_index]

