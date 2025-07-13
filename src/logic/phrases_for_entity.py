from src.shemes import Project


def phases_for_entity(dataset: dict, project: Project):
    phrases = {"entities": {}}
    for intent in project.intents:
        phrases[intent] = [] # type: ignore
        phrases["entities"][intent] = []

    for el in dataset["hand-data"]:
        phrases[el["classification"]].append({ # type: ignore
            "text": el["text"]
        })
        for entity in el["slots"]:
            phrases[el["classification"]][-1][entity["entity"]] = entity["value"]
            if entity["entity"] not in phrases["entities"][el["classification"]]:
                phrases["entities"][el["classification"]].append(entity["entity"])

    return phrases