from random import choice

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