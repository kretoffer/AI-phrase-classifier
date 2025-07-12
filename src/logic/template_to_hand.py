def template2hand(template: dict):
    data = []
    for text in template["texts"]:
        if len(template["entitys"]) == 1:
            key = list(template["entitys"].keys())[0]
            for el in list(template["entitys"].values())[0]:
                phrase = text.replace(f"${key}", el["text"])
                data.append({
                    "classification" : template["classification"],
                    "slots": [{"entity":key,"value":el["value"]}],
                    "text": phrase
                })
    return data