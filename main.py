import json

from src.template_to_hand import template2hand

def main(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        data: dict = json.load(file)
    
    for template in data["template-data"]:
        data["hand-data"].extend(template2hand(template))
    del(data["template-data"])

    phrases = [el["text"] for el in data["hand-data"]]
    print(phrases)



if __name__ == "__main__":
    main("input.json")