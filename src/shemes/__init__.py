import re
from typing import List, Literal, Tuple
from pydantic import BaseModel, Field


class Project(BaseModel):
    name: str
    status: Literal["work", "educated", "off", "error"]
    intents: List[str]
    entities: List[str]

class SomeEntity(BaseModel):
    name: str

class DeletebleEntity(SomeEntity):
    delete: Literal["Delete"] = Field("Delete")

class Slot(BaseModel):
    entity: str
    start: int
    end: int

class FormSlot(Slot):
    value: str

class DatasetData(BaseModel):
    text: str
    classification: str
    slots: List[Slot]

class UpdateDatasetFormData(BaseModel):
    text: str
    classification: str
    slots: List[FormSlot] 

    def to_dataset_data(self) -> Tuple[DatasetData, dict]:
        dataset_data = DatasetData(
            text=re.sub(r'[^\w\s]', '', self.text.lower(), flags=re.UNICODE),
            classification=self.classification,
            slots=[Slot(entity=el.entity, start=el.start, end=el.end) for el in self.slots]
        )
        new_synonimz = {}
        for el in self.slots:
            synonim = self.text[el.start:el.end]
            if synonim != el.value:
                new_synonimz[synonim] = el.value
        return dataset_data, new_synonimz
    
class TemplateEntity(BaseModel):
    text: str
    value: str
    
class DatasetTemplateData(BaseModel):
    classification: str
    texts: List[str]
    entitys: dict #Dict[str, List[TemplateEntity]]
