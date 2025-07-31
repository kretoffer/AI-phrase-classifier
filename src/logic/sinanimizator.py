def sinanimizate(synanimz: dict, word: str) -> str:
    return synanimz[word] if word in synanimz else word
