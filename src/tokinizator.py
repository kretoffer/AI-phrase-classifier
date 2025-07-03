from typing import List
import re

def get_vocab(phrases: List[str]):
    vocab = set()
    for el in phrases:
        text = re.sub(r'[^\w\s]', '', el.lower(), flags=re.UNICODE)
        words = text.split(" ")
        vocab.update(words)
    return vocab


def get_word2idx(vocab):
    return {word: idx+1 for idx, word in enumerate(vocab)}

def tokenize(text, vocab, max_len=32):
    tokens = text.lower().split()
    token_ids = [vocab.get(word, 0) for word in tokens] #0 — для неизвестных слов
    token_ids = token_ids[:max_len] + [0] * max(0, max_len - len(token_ids)) #паддинг и обрезка
    return token_ids