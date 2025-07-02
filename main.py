import json

from src.template_to_hand import template2hand
from src.tokinizator import *

def main(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        data: dict = json.load(file)
    
    for template in data["template-data"]:
        data["hand-data"].extend(template2hand(template))
    del(data["template-data"])

    phrases = [el["text"] for el in data["hand-data"]]
    phrases = [re.sub(r'[^\w\s]', '', phrase.lower(), flags=re.UNICODE) for phrase in phrases]

    vocab = get_vocab(phrases)
    idx = get_word2idx(vocab)

    tokenize_phrases = [tokenize(phrase, idx) for phrase in phrases]
    print(tokenize_phrases)



if __name__ == "__main__":
    main("input.json")