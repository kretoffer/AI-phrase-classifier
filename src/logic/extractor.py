import json
import os
import re

import numpy as np
import yaml
from src.logic.neuron_activation import activate
from src.shemes import Project
from src.logic.sinanimizator import sinanimizate


def extract(project_path: str, emb_phrase, intent: str, question: str):
    entities = [f.replace(".npz", "") for f in os.listdir(f"{project_path}/models/{intent}") if f.endswith(".npz")]

    slots = []
    for entity in entities:
        slots.append({entity: extract_entity(project_path, emb_phrase, intent, entity, question)})
    
    return slots

def extract_entity(project_path: str, emb_phrase, intent: str, entity: str, question: str):
    with open(f"{project_path}/sinonimz.json", "r", encoding="utf-8") as f:
        sinonimz = json.load(f)

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

    output = activate(output_raw, project.activation_method)
    output = np.array([x.item() for x in output])
    output = (output > 0.5).astype(int)

    words = re.sub(r'[^\w\s]', '', question.lower(), flags=re.UNICODE).split()
    words = np.array(words[:32] + [""] * max(0, 32 - len(words)))

    extracted_entity = " ".join(words[output.astype(bool)].tolist())

    return sinanimizate(sinonimz, extracted_entity)
