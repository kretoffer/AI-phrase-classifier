import json
from fastapi import APIRouter
import yaml

from config import projects_dir

from src.logic.sinanimizator import sinanimizate

router = APIRouter()

@router.get("/project-info/{name}", tags=["api"])
def project_info(name: str):
    return yaml.load(open(f"{projects_dir}/{name}/config.yaml", "r"), Loader=yaml.SafeLoader)

@router.get("/dataset-hand-element-data/{project_name}/{element_id}", tags=["api"])
def dataset_hand_element_info(project_name: str, element_id: int):
    with open(f"{projects_dir}/{project_name}/dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
    with open(f"{projects_dir}/{project_name}/sinonimz.json", "r", encoding="utf-8") as f:
        sinonimz = json.load(f)
    element = dataset["hand-data"][element_id]
    text_split =  element["text"].split(" ")
    slots = []
    for slot in element["slots"]:
        start = len(" ".join(text_split[0:slot["tokens"][0]]))+1
        entity = " ".join(text_split[slot["tokens"][0]:slot["tokens"][-1]+1])
        slots.append({
            "start": start,
            "end": len(entity)+start,
            "entity": slot["entity"],
            "value": sinanimizate(sinonimz, entity)
        })
    element["slots"] = slots
    return element
