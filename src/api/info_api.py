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
    text =  element["text"]
    for slot in element["slots"]:
        slot["value"] = sinanimizate(sinonimz, text[slot["start"]:slot["end"]])
    return element

@router.get("/dataset-template-element-data/{project_name}/{element_id}", tags=["api"])
def dataset_template_element_info(project_name: str, element_id: int):
    with open(f"{projects_dir}/{project_name}/dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
    return dataset["template-data"][element_id]
