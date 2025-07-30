import json
import spacy

from src.logic.sinanimizator import sinanimizate


def extract(project_path: str, intent: str, question: str):
    nlp2 = spacy.load(f"{project_path}/{intent}")
    doc = nlp2(question)

    with open(f"{project_path}/sinonimz.json", "r", encoding="utf-8") as f:
        sinonimz = json.load(f)
    
    return [{"value": sinanimizate(sinonimz, ent.text), "role": ent.label_} for ent in doc.ents]
