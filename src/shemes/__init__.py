import re
from typing import List, Literal, Tuple
from pydantic import BaseModel, Field


class Project(BaseModel):
    name: str
    status: Literal["work", "educated", "off", "error"]
    hidden_layer: int = Field(50, gt=0)
    epochs: int = Field(0, gt=-1)
    learning_rate: float = Field(0.01, gt=0)
    embedding_dim: int = Field(32, gt=0)
    intents: List[str]
    activation_method: Literal["sigmoid", "relu", "tanh", "leaky relu", "softmax", "swish", "mish"]
    entities: List[str]

class SomeEntity(BaseModel):
    name: str

class Slot(BaseModel):
    entity: str

class FormSlot(Slot):
    start: int
    end: int
    value: str

class DatasetSlot(Slot):
    tokens: List[int]

class DatasetData(BaseModel):
    text: str
    classification: str
    slots: List[DatasetSlot]

class UpdateDatasetFormData(BaseModel):
    text: str
    classification: str
    slots: List[FormSlot] 

    def to_dataset_data(self) -> Tuple[DatasetData, dict]:
        dataset_data = DatasetData(
            text=re.sub(r'[^\w\s]', '', self.text.lower(), flags=re.UNICODE),
            classification=self.classification,
            slots=[]
        )
        new_synonimz = {}
        for el in self.slots:
            entity = dataset_data.text[el.start:el.end]
            entity_split = entity.split()
            tokens = []
            for entity in entity_split:
                for i, word in enumerate(dataset_data.text.split()):
                    if entity in word:
                        tokens.append(i)
            synonim = " ".join([dataset_data.text.split()[token] for token in tokens])
            if synonim != el.value:
                new_synonimz[synonim] = el.value
            dataset_data.slots.append(DatasetSlot(entity=el.entity, tokens=tokens))
        return dataset_data, new_synonimz
