def template2hand(template: dict):
    data = []
    for text in template["texts"]:
        if len(template["entitys"]) == 1:
            key = list(template["entitys"].keys())[0]
            for el in list(template["entitys"].values())[0]:
                phrase = text.replace(f"${key}", el["text"])
                phrase_split = phrase.split()
                entity_split = el["text"].split()

                tokens = []
                for i, phr in enumerate(phrase_split):
                    for enity in entity_split:
                        if enity == phr:
                            tokens.append(i)

                data.append({
                    "classification" : template["classification"],
                    "slots": [{"entity":key, "tokens": tokens}],
                    "text": phrase
                })
    return data