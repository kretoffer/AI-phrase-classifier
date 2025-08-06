from typing import Dict, List, Literal

from pydantic import BaseModel, Field

class FormAddToDatasetHand(BaseModel):
    classification: str
    slots: List[Dict[str, str]]
    text: str
