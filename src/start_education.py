from src.vocab_from_input import get_vocab_from_hand_data, get_hand_data
from src.embedding import generate_matrix, embedding
from education import educate
from tokinizator import tokenize

import json
import numpy as np
import os
import yaml

def start_education(path_to_project: str):
    with open(f"{path_to_project}/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    intents = config["intents"]

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
    embedding_matrix = generate_matrix(len(vocab), config["embedding_dim"])

    data = []
    for el in dataset["hand-data"]:
        tokens = tokenize(el["text"], vocab)
        emb = embedding(embedding_matrix, tokens)
        label = np.zeros(len(intents), dtype=np.float64)
        label[intents.index(el["classification"])] = 1.0
        data.append((emb, label))

    educate(data, embedding_matrix, len(vocab)*config["embedding_dim"], config["hidden_layer"], len(config["intents"]))
    