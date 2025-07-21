import itertools

def template2hand(template: dict):
    data = []
    for text in template["texts"]:
        if not template["entitys"]:
            data.append({
                "classification" : template["classification"],
                "slots": [],
                "text": text
            })
        else:
            entities = template["entitys"].keys()
            value_lists = list(template["entitys"].values())
            combinations = list(itertools.product(*value_lists))

            for combination in combinations:
                phrase = text
                tokens = []
                for i, entity in enumerate(entities):
                    phrase = phrase.replace(f"${entity}", combination[i]["text"])
                phrase_split = phrase.split()
                for i, entity in enumerate(entities):
                    entity_split = combination[i]["text"].split()

                    token = []
                    for j, phr in enumerate(phrase_split):
                        for en in entity_split:
                            if en == phr:
                                token.append(j)
                    tokens.append({"entity": entity, "tokens": token})
                data.append({
                    "classification" : template["classification"],
                    "slots": tokens,
                    "text": phrase
                })
    return data