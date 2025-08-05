import json
import multiprocessing
import os
from hashlib import md5

import yaml

from config import projects_dir
from src.logic.education import educate_classifier, educate_entity_extractor
from src.logic.parse_dataset import parse_dataset
from src.logic.template_to_hand import get_hand_data
from src.shemes import Project


def split_list(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def hash_dict_json(d):
    dict_str = json.dumps(d, sort_keys=True)
    return md5(dict_str.encode()).hexdigest()


def hash_list_of_dicts(lst):
    serialized = json.dumps(lst, sort_keys=True)
    return md5(serialized.encode()).hexdigest()


def start_educate(path_to_project: str):
    project = Project.model_validate(
        yaml.load(open(f"{path_to_project}/config.yaml", "r"), Loader=yaml.SafeLoader)
    )
    project.status = "educated"

    with open(f"{path_to_project}/dataset.json", "r", encoding="utf-8") as file:
        dataset: dict = json.load(file)

    dataset_hash = hash_dict_json(dataset)
    with open(f"{path_to_project}/educated.json", "r+", encoding="utf-8") as f:
        educated = json.load(f)
        if "classifier" in educated and educated["classifier"] == dataset_hash:
            print("The classifier does not need training")
            return

    with open(f"{path_to_project}/sinonimz.json", "r+", encoding="utf-8") as f:
        sinonimz = json.load(f)
        for el in dataset["template-data"]:
            for entity in el["entitys"]:
                for elem in el["entitys"][entity]:
                    if elem["text"] != elem["value"]:
                        sinonimz[elem["text"]] = elem["value"]
        f.seek(0)
        f.truncate()
        json.dump(sinonimz, f, ensure_ascii=False, indent=1)

    dataset = get_hand_data(dataset)
    if len(dataset["hand-data"]) == 0:
        return {"error": "empty dataset"}

    with open(f"{path_to_project}/config.yaml", "w", encoding="utf-8") as f:
        project.intents, project.entities = parse_dataset(dataset, project)
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)

    texts = [el["text"] for el in dataset["hand-data"]]
    labels = [el["classification"] for el in dataset["hand-data"]]

    classifier_data = (texts, labels, path_to_project)

    extractors_data = {}
    for intent in project.intents:
        extractors_data[intent] = []
    for el in dataset["hand-data"]:
        extractors_data[el["classification"]].append(el)

    data_for_entity_education, new_educated = start_educate_extractors(
        project, extractors_data
    )

    start_education_threads(classifier_data, data_for_entity_education, project)

    new_educated["classifier"] = dataset_hash
    with open(f"{path_to_project}/educated.json", "w", encoding="utf-8") as f:
        json.dump(new_educated, f)

    print(f"{project.name} was educated")

    project.status = "work"
    with open(f"{path_to_project}/config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)


def start_educate_extractors(project: Project, phrases: dict):
    data_for_entity_education = {}
    with open(
        f"{projects_dir}/{project.name}/educated.json", "r", encoding="utf-8"
    ) as f:
        educated = json.load(f)
    for intent in project.intents:
        if not os.path.exists(f"{projects_dir}/{project.name}/models/{intent}"):
            os.makedirs(f"{projects_dir}/{project.name}/models/{intent}")
        dataset_hash = hash_list_of_dicts(phrases[intent])
        if intent in educated and educated[intent] == dataset_hash:
            continue

        dataset = []
        for el in phrases[intent]:
            body = {
                "entities": [
                    (slot["start"], slot["end"], slot["entity"]) for slot in el["slots"]
                ]
            }
            dataset.append((el["text"], body))

        data_for_entity_education[intent] = dataset
        educated[intent] = dataset_hash

    return data_for_entity_education, educated


def start_education_threads(
    classifier_data: tuple, extractors_data: dict, project: Project
):
    max = os.cpu_count() if os.cpu_count() else 1
    queue = split_list(list(range(-1, len(extractors_data))), max)

    for line in queue:
        threads = []
        for el in line:
            if el == -1:
                t = multiprocessing.Process(
                    target=educate_classifier, args=classifier_data
                )
            else:
                args = list(extractors_data.keys())
                intent = args[el]
                t = multiprocessing.Process(
                    target=educate_entity_extractor,
                    args=(
                        intent,
                        extractors_data[intent],
                        project,
                        f"{projects_dir}/{project.name}",
                    ),
                )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
