from src.shemes import Project
from src.logic.vocab_from_input import get_vocab_from_hand_data, get_hand_data
from src.logic.embedding import generate_matrix, embedding
from src.logic.education import educate_classifier, educate_entity_extractor
from src.logic.tokinizator import tokenize
from src.logic.parse_dataset import parse_dataset
from src.logic.phrases_for_entity import phases_for_entity
from src.logic.auto_select_epochs import auto_select_epochs
from src.logic.optimize_dataset import optimize_dataset

from config import projects_dir

import json
import numpy as np
import os
import yaml
import pickle

def start_educate(path_to_project: str):
    project = Project.model_validate(yaml.load(open(f"{path_to_project}/config.yaml", "r"), Loader=yaml.SafeLoader))
    project.status = "educated"

    with open(f"{path_to_project}/dataset.json", 'r', encoding='utf-8') as file:
        dataset: dict = json.load(file)

    with open(f"{path_to_project}/sinonimz.json", "r+", encoding="utf-8") as f:
        sinonimz = json.load(f)
        for el in dataset["template-data"]:
            for entity in el["entitys"]:
                for elem in el["entitys"][entity]:
                    sinonimz[elem["text"]] = elem["value"]
        f.seek(0)
        f.truncate()
        json.dump(sinonimz, f, ensure_ascii=False, indent=1)

    dataset = get_hand_data(dataset)

    with open(f"{path_to_project}/config.yaml", "w", encoding="utf-8") as f:
        project.intents, project.entities = parse_dataset(dataset, project)
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)

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

    phrases = phases_for_entity(dataset, project) 
    dataset = optimize_dataset(phrases)

    data = []
    for el in dataset["hand-data"]:
        tokens = tokenize(el["text"], vocab)
        emb = embedding(embedding_matrix, tokens)
        label = np.array([[0] for _ in range(0, len(project.intents))])
        label[project.intents.index(el["classification"])] = 1.0
        data.append((emb, label, tokens))


    epochs = project.epochs if project.epochs else auto_select_epochs(len(data), project.learning_rate)
    educate_classifier(data, embedding_matrix, project.embedding_dim*32, project.hidden_layer, len(project.intents), path_to_project, project.activation_method, epochs, project.learning_rate) # type: ignore
    start_educate_extractors(project, phrases, embedding_matrix, vocab)

    print(f"{project.name} was educated")
    
    project.status = "work"
    with open(f"{path_to_project}/config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)  


def start_educate_extractors(project: Project, phrases: dict, embedding_matrix, vocab): 

    for intent in project.intents:
        if not os.path.exists(f"{projects_dir}/{project.name}/models/{intent}"):
            os.makedirs(f"{projects_dir}/{project.name}/models/{intent}")
        if not phrases["entities"][intent]:
            continue
        entities = phrases["entities"][intent]
        for entity in entities:
            data = []
            for el in phrases[intent]:
                data.append((el["text"], el[entity]))

            entity_dataset = []
            for el in data:
                tokens = tokenize(el[0], vocab)
                emb = embedding(embedding_matrix, tokens)
                label = np.array([[0] for _ in range(0, 32)])
                for token in el[1]:
                    label[token] = 1.0
                entity_dataset.append((emb, label))
            
            epochs = project.epochs if project.epochs else auto_select_epochs(len(entity_dataset), project.learning_rate)

            educate_entity_extractor(entity_dataset, project.embedding_dim*32, project.hidden_layer, 32, f"{projects_dir}/{project.name}/models", project.activation_method, epochs, entity, intent, project.learning_rate)
            
