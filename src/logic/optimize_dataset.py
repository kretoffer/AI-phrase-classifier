from random import choice
from typing import List

def optimize_dataset(phrases: dict) -> dict:
    dataset = {"hand-data": [], "template-data": []}
    slots = {}
    for intent in phrases["entities"]:
        slots[intent] = []
        for el in phrases[intent]:
            slot = {
                "classification": intent,
                "text": el["text"],
                "slots": []
            }
            for entity in phrases["entities"][intent]:
                slot["slots"].append({
                    "entity": entity,
                    "tokens": el[entity]
                })

            slots[intent].append(slot)
    
    dataset_len = max([len(slots[intent]) for intent in phrases["entities"]])
    
    for intent in phrases["entities"]:
        while len(slots[intent]) < dataset_len and len(slots[intent]) > 0:
            slots[intent].append(choice(slots[intent]))

    for el in slots.values():
        dataset["hand-data"].extend(el)

    return dataset

def optimize_extractor_dataset(phrases: List[dict], entity: str):
    phrases_data = {}
    for el in phrases:
        tokens = tuple(el[entity])
        if tokens not in phrases_data:
            phrases_data[tokens] = []
        phrases_data[tokens].append(el["text"])
    
    t = [len(token) for token in phrases_data.values()]
    phrases_len = max(t)

    for token in phrases_data.keys():
        while len(phrases_data[token]) < phrases_len and len(phrases_data[token]) > 0:
            phrases_data[token].append(choice(phrases_data[token]))

    dataset = []
    for token in phrases_data:
        for el in phrases_data[token]:
            dataset.append({"text": el, entity: token})

    return dataset, sum(t)
