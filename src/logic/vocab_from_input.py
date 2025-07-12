from src.logic.template_to_hand import template2hand
from src.logic.tokinizator import *

def get_vocab_from_hand_data(data: dict):
    phrases = [el["text"] for el in data["hand-data"]]

    vocab = get_vocab(phrases)
    idx = get_word2idx(vocab)

    return idx

def get_hand_data(data):
    for template in data["template-data"]:
        data["hand-data"].extend(template2hand(template))
    del(data["template-data"])
    return data