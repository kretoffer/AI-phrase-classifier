import itertools


def template2hand(template: dict):
    data = []
    for text in template["texts"]:
        if not template["entitys"]:
            data.append(
                {
                    "classification": template["classification"],
                    "slots": [],
                    "text": text,
                }
            )
        else:
            entities = template["entitys"].keys()
            value_lists = list(template["entitys"].values())
            combinations = list(itertools.product(*value_lists))

            for combination in combinations:
                phrase = text
                slots = []
                for i, entity in enumerate(entities):
                    phrase = phrase.replace(f"${entity}", combination[i]["text"])
                for i, entity in enumerate(entities):
                    start = len(phrase.split(combination[i]["text"])[0])
                    end = len(combination[i]["text"]) + start
                    slots.append({"entity": entity, "start": start, "end": end})
                data.append(
                    {
                        "classification": template["classification"],
                        "slots": slots,
                        "text": phrase,
                    }
                )
    return data


def get_hand_data(data):
    if "template-data" not in data:
        return data
    for template in data["template-data"]:
        data["hand-data"].extend(template2hand(template))
    del data["template-data"]
    return data
