from typing import Dict, List, Literal
from enum import Enum
from pydantic import BaseModel, Field

class EditForm(BaseModel):
    #name: Optional[str] = Field("test", description="name of the project", title="Project name")
    hidden_layer: int = Field(50, gt=0, title="hidden neurouns", description="the count of neurons in hidden layer")
    epochs: int = Field(0, title="epochs", description="try 0 to auto set")
    learning_rate: float = Field(0.01, gt=0)
    embedding_dim: int = Field(32)
    activation_method: Literal["relu", "sigmoid", "tanh", "leaky relu", "softmax", "swish", "mish"] = Field("relu")

class FormAddToDatasetHand(BaseModel):
    classification: str
    slots: List[Dict[str, str]]
    text: str
