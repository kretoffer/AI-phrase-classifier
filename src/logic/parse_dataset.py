from typing import List, Tuple

from src.logic.vocab_from_input import get_hand_data



def parse_dataset(dataset: dict, project) -> Tuple[List[str], List[str]]:
    dataset = dataset.copy()
    dataset = get_hand_data(dataset)

    for el in dataset["hand-data"]:
        if el["classification"] not in project.intents:
            project.intents.append(el["classification"])
        for slot in el["slots"]:
            if slot["entity"] not in project.entities:
                project.entities.append(slot["entity"])

    return project.intents, project.entities
