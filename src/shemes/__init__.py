from typing import List, Literal
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
