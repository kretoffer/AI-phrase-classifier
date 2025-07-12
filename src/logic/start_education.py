from src.shemes import Project
from src.logic.vocab_from_input import get_vocab_from_hand_data, get_hand_data
from src.logic.embedding import generate_matrix, embedding
from src.logic.education import educate
from src.logic.tokinizator import tokenize
from src.logic.parse_dataset import parse_dataset

import json
import numpy as np
import os
import yaml

def start_educate(path_to_project: str):
    project = Project.model_validate(yaml.load(open(f"{path_to_project}/config.yaml", "r"), Loader=yaml.SafeLoader))

    with open(f"{path_to_project}/dataset.json", 'r', encoding='utf-8') as file:
        dataset: dict = json.load(file)
    dataset = get_hand_data(dataset)

    with open(f"{path_to_project}/vocab.json", "w", encoding="utf-8") as f:
        vocab = get_vocab_from_hand_data(dataset)
        data = vocab

        json.dump(data, f, ensure_ascii=False)

    #TODO
    # if not os.path.exists(f"{path_to_project}/embedding.bin"):
    #     embedding_matrix = generate_matrix(len(vocab), 32) 
    # else:
    #     embedding_matrix = np.load(f"{path_to_project}/embedding.bin")  
    #     #Тут должна быть логика добавления новых векторов для новых слов, так же и с словарем
    embedding_matrix = generate_matrix(len(vocab), project.embedding_dim)

    data = []
    for el in dataset["hand-data"]:
        tokens = tokenize(el["text"], vocab)
        emb = embedding(embedding_matrix, tokens)
        label = np.array([[0] for _ in range(0, len(project.intents))])
        label[project.intents.index(el["classification"])] = 1.0
        data.append((emb, label, tokens))

    educate(data, embedding_matrix, project.embedding_dim**2, project.hidden_layer, len(project.intents), path_to_project, project.activation_method, project.epochs) # type: ignore
