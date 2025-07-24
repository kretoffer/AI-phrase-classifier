import json
import os
from typing import Annotated, List
from uuid import uuid4
from fastapi import APIRouter, Form, UploadFile
from fastui import FastUI
import yaml
import re

from fastui import components as c
from fastui.events import GoToEvent
from fastui.forms import FormFile

from config import projects_dir

from src.logic.parse_dataset import parse_dataset
from src.shemes import Project, DatasetData, UpdateDatasetFormData, DatasetSlot

router = APIRouter()

@router.post("/update-dataset/{name}", tags=["api"])
async def update_dataset(name, data: UpdateDatasetFormData):
    body, new_synonimz = data.to_dataset_data()
    body = body.model_dump()

    if not os.path.exists(f"{projects_dir}/{name}"):
        return {"error": "no such project exists"}
    
    with open(f"{projects_dir}/{name}/sinonimz.json", "r+", encoding="utf-8") as f:
        if file := f.read():
            synonimz = json.loads(file)
        else:
            synonimz = {}
        synonimz.update(new_synonimz)
        f.seek(0)
        f.truncate()
        json.dump(synonimz, f, ensure_ascii=False, indent=1)
    
    with open(f"{projects_dir}/{name}/dataset.json", "r+", encoding="utf-8") as f:
        dataset = json.load(f)

        data_hand = {"hand-data": [body], "template-data": []}

        with open(f"{projects_dir}/{name}/config.yaml", "r+", encoding="utf-8") as conf:
            project = Project.model_validate(yaml.load(conf, Loader=yaml.SafeLoader))
            project.intents, project.entities = parse_dataset(data_hand, project)
            conf.seek(0)
            conf.truncate()
            yaml.dump(project.model_dump(), conf, allow_unicode=True, sort_keys=False)

        dataset["hand-data"].append(body)

        f.seek(0)
        f.truncate()
        json.dump(dataset, f, ensure_ascii=False, indent=1)

    return 

@router.post("/update-dataset-file/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["api"])
async def update_dataset_with_file(name, files: List[Annotated[UploadFile, FormFile(accept="application/json")]] = Form(alias="dataset")):

    if not os.path.exists(f"{projects_dir}/{name}"):
        return {"error": "no such project exists"}
    
    if not files:
        return {"error": "no such files in form"}
    
    data = {}
    for file in files:
        f = await file.read()
        data.update(json.loads(f))

    with open(f"{projects_dir}/{name}/config.yaml", "r+", encoding="utf-8") as f:
        project = Project.model_validate(yaml.load(f, Loader=yaml.SafeLoader))
        project.intents, project.entities = parse_dataset(data, project)
        f.seek(0)
        f.truncate()
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)
    
    with open(f"{projects_dir}/{name}/dataset.json", "r+", encoding="utf-8") as f:
        dataset = json.load(f)
        dataset["hand-data"].extend(data["hand-data"])
        dataset["template-data"].extend(data["template-data"])
        f.seek(0)
        f.truncate()
        json.dump(dataset, f, ensure_ascii=False, indent=1)

    return [c.FireEvent(event=GoToEvent(url=f"/web/project/{name}/edit/dataset?u={uuid4()}"))]


@router.post("/replace-dataset-file/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["api"])
async def replace_dataset_with_file(name, file: Annotated[UploadFile, FormFile(accept="application/json")] = Form(alias="dataset")):

    if not os.path.exists(f"{projects_dir}/{name}"):
        return {"error": "no such project exists"}
    
    dataset = json.loads(await file.read())
    if "hand-data" not in dataset:
        dataset["hand-data"] = []
    if "template-data" not in dataset:
        dataset["template-data"] = []
    with open(f"{projects_dir}/{name}/config.yaml", "r+", encoding="utf-8") as f:
        project = Project.model_validate(yaml.load(f, Loader=yaml.SafeLoader))
        project.intents, project.entities = parse_dataset(dataset, project)
        f.seek(0)
        f.truncate()
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)
    
    with open(f"{projects_dir}/{name}/dataset.json", "r+", encoding="utf-8") as f:
        f.seek(0)
        f.truncate()
        json.dump(dataset, f, ensure_ascii=False, indent=1)

    return [c.FireEvent(event=GoToEvent(url=f"/web/project/{name}/edit/dataset?u={uuid4()}"))]
