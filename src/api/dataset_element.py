import json
import os

from fastapi import APIRouter

from config import projects_dir
from src.shemes import DatasetTemplateData, UpdateDatasetFormData

router = APIRouter()


@router.delete("/delete-hand-element/{project}/{id}", tags=["api"])
def delete_hand_element(project: str, id: int):
    with open(f"{projects_dir}/{project}/dataset.json", "r+", encoding="utf-8") as f:
        dataset = json.load(f)
        del dataset["hand-data"][id]
        f.seek(0)
        f.truncate()
        json.dump(dataset, f, ensure_ascii=False, indent=1)


@router.post("/update-hand-element/{project}/{id}", tags=["api"])
def update_hand_element(project: str, id: int, form_data: UpdateDatasetFormData):
    if not os.path.exists(f"{projects_dir}/{project}"):
        return {"error": "no such project exists"}

    with open(f"{projects_dir}/{project}/dataset.json", "r+", encoding="utf-8") as f:
        dataset = json.load(f)
        body, new_synonimz = form_data.to_dataset_data()
        dataset["hand-data"][id] = body.model_dump()
        f.seek(0)
        f.truncate()
        json.dump(dataset, f, ensure_ascii=False, indent=1)

    with open(f"{projects_dir}/{project}/sinonimz.json", "r+", encoding="utf-8") as f:
        if file := f.read():
            synonimz = json.loads(file)
        else:
            synonimz = {}
        synonimz.update(new_synonimz)
        f.seek(0)
        f.truncate()
        json.dump(synonimz, f, ensure_ascii=False, indent=1)


@router.delete("/delete-template-element/{project}/{id}", tags=["api"])
def delete_template_element(project: str, id: int):
    with open(f"{projects_dir}/{project}/dataset.json", "r+", encoding="utf-8") as f:
        dataset = json.load(f)
        del dataset["template-data"][id]
        f.seek(0)
        f.truncate()
        json.dump(dataset, f, ensure_ascii=False, indent=1)


@router.post("/update-template-element/{project}/{id}", tags=["api"])
def update_template_element(project: str, id: int, form_data: DatasetTemplateData):
    if not os.path.exists(f"{projects_dir}/{project}"):
        return {"error": "no such project exists"}

    with open(f"{projects_dir}/{project}/dataset.json", "r+", encoding="utf-8") as f:
        dataset = json.load(f)
        dataset["template-data"][id] = form_data.model_dump()
        f.seek(0)
        f.truncate()
        json.dump(dataset, f, ensure_ascii=False, indent=1)
