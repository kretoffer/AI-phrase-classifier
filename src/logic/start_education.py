from typing import List
from src.shemes import Project
from src.logic.vocab_from_input import get_vocab_from_hand_data, get_hand_data
from src.logic.embedding import generate_matrix, embedding
from src.logic.education import educate_classifier, educate_entity_extractor
from src.logic.tokinizator import tokenize
from src.logic.parse_dataset import parse_dataset
from src.logic.phrases_for_entity import phases_for_entity
from src.logic.auto_select_epochs import auto_select_epochs
from src.logic.optimize_dataset import optimize_dataset, optimize_extractor_dataset

from config import projects_dir

import json
import numpy as np
import os
import yaml
import multiprocessing
from hashlib import md5

def split_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def hash_dict_json(d):
    dict_str = json.dumps(d, sort_keys=True)
    return md5(dict_str.encode()).hexdigest()

def hash_list_of_dicts(lst):
    serialized = json.dumps(lst, sort_keys=True)
    return md5(serialized.encode()).hexdigest()

def project_config_hash(project: Project):
    hashable_project = project.model_dump()
    del hashable_project["name"], hashable_project["status"], hashable_project["intents"], hashable_project["entities"]
    return hash_dict_json(hashable_project)

def start_educate(path_to_project: str):
    project = Project.model_validate(yaml.load(open(f"{path_to_project}/config.yaml", "r"), Loader=yaml.SafeLoader))
    project.status = "educated"

    with open(f"{path_to_project}/dataset.json", 'r', encoding='utf-8') as file:
        dataset: dict = json.load(file)

    dataset_hash = hash_dict_json(dataset)
    with open(f"{path_to_project}/educated.json", "r+", encoding="utf-8") as f:
        educated = json.load(f)
        if "classifier" in educated and educated["classifier"] == dataset_hash \
        and "project_data" in educated and educated["project_data"] == project_config_hash(project):
            print("The classifier does not need training")
            return

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
    classifier_data = (data, embedding_matrix, project.embedding_dim*32, project.hidden_layer, len(project.intents), path_to_project, project.activation_method, epochs, project.learning_rate) # type: ignore
    data_for_entity_education, new_educated = start_educate_extractors(project, phrases, embedding_matrix, vocab)

    start_education_threads(classifier_data, data_for_entity_education)

    new_educated["classifier"] = dataset_hash
    new_educated["project_data"] = project_config_hash(project)
    with open(f"{path_to_project}/educated.json", "w", encoding="utf-8") as f:
        json.dump(new_educated, f)

    print(f"{project.name} was educated")
    
    project.status = "work"
    with open(f"{path_to_project}/config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)  


def start_educate_extractors(project: Project, phrases: dict, embedding_matrix, vocab): 
    data_for_entity_education = []
    with open(f"{projects_dir}/{project.name}/educated.json", "r", encoding="utf-8") as f:
        educated = json.load(f)
    for intent in project.intents:
        if not os.path.exists(f"{projects_dir}/{project.name}/models/{intent}"):
            os.makedirs(f"{projects_dir}/{project.name}/models/{intent}")
        if not phrases["entities"][intent]:
            continue
        dataset_hash = hash_list_of_dicts(phrases[intent])
        if intent in educated and educated[intent] == dataset_hash\
            and "project_data" in educated and educated["project_data"] == project_config_hash(project):
            continue
        entities = phrases["entities"][intent]
        for entity in entities:
            data = []
            optimized_phrases, dataset_len = optimize_extractor_dataset(phrases[intent], entity)
            for el in optimized_phrases:
                data.append((el["text"], el[entity]))

            entity_dataset = []
            for el in data:
                tokens = tokenize(el[0], vocab)
                emb = embedding(embedding_matrix, tokens)
                label = np.array([[0] for _ in range(0, 32)])
                for token in el[1]:
                    label[token] = 1.0
                entity_dataset.append((emb, label))
            
            epochs = project.epochs if project.epochs else auto_select_epochs(dataset_len, project.learning_rate)

            data_for_entity_education.append((entity_dataset, project.embedding_dim*32, project.hidden_layer, 32, f"{projects_dir}/{project.name}/models", project.activation_method, epochs, entity, intent, project.learning_rate))
        educated[intent] = dataset_hash

    return data_for_entity_education, educated


def start_education_threads(classifier_data: tuple, extractors_data: List[tuple]):
    max = os.cpu_count() if os.cpu_count() else 1
    queue = split_list(list(range(-1, len(extractors_data))), max)

    for line in queue:
        threads = []
        for el in line:
            if el == -1:
                t = multiprocessing.Process(target=educate_classifier, args=classifier_data)
            else:
                t = multiprocessing.Process(target=educate_entity_extractor, args=extractors_data[el])
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()

