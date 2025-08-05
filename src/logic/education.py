import random
from typing import List

import joblib
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from spacy.training.example import Example
from spacy.util import minibatch
from thinc.schedules import compounding

from src.shemes import Project


def educate_classifier(texts, labels, project_path):
    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=200)),
        ]
    )
    pipe.fit(texts, labels)
    joblib.dump(pipe, f"{project_path}/classifier")


def educate_entity_extractor(
    intent: str, data: List[tuple], project: Project, project_path: str
):
    nlp = spacy.blank("ru")
    ner = nlp.add_pipe("ner", last=True)
    for entity in project.entities:
        ner.add_label(entity)  # type: ignore

    optimizer = nlp.begin_training()

    for _ in range(30):
        random.shuffle(data)
        batches = minibatch(data, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp.update([example], sgd=optimizer)

    nlp.to_disk(f"{project_path}/{intent}")
