import os
import platform
import subprocess
from fastapi import APIRouter, Form
from fastapi.responses import FileResponse
from fastui import FastUI
import yaml

from fastui import components as c
from fastui.events import GoToEvent

from config import projects_dir

from src.logic.start_education import start_educate
from src.shemes import Project


router = APIRouter()

open_file_methods = {
    "Windows": lambda path: subprocess.Popen(f'explorrer /select, "{path}"'),
    "Darwin": lambda path: subprocess.run(["open", path]),
    "Linux": lambda path: subprocess.run(["xdg-open", path])
}


@router.post("/new-project", response_model=FastUI, response_model_exclude_none=True, tags=["api"])
def new_project(name:str = Form("test", alias="project-name")):

    if os.path.exists(f"{projects_dir}/{name}"):
        return {"error": "a project with this name already exists"}
    
    os.makedirs(f"{projects_dir}/{name}")
    os.makedirs(f"{projects_dir}/{name}/models")
    
    with open(f"{projects_dir}/{name}/config.yaml", "w", encoding="utf-8") as f:
        project=Project(
            name=name,
            status="off",
            hidden_layer=50,
            epochs=0,
            learning_rate=0.01,
            embedding_dim=32,
            intents=[],
            activation_method="sigmoid",
            entities=[]
            )
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)

    with open(f"{projects_dir}/{name}/dataset.json", "x", encoding="utf-8") as f:
        f.write('{"hand-data": [], "template-data": []}')
    with open(f"{projects_dir}/{name}/educated.json", "x", encoding="utf-8") as f:
        f.write('{}')

    
    return [c.FireEvent(event=GoToEvent(url=f"/web/project/{name}"))]

@router.get("/download-dataset/{name}")
def download_dataset(name: str):
    return FileResponse(
        path=f"{projects_dir}/{name}/dataset.json",
        filename="dataset.json",
        media_type="application/json"
    )

@router.get("/open-project-dir/{name}")
def open_project_dir(name: str):
    open_file_methods[platform.system()](f"{projects_dir}/{name}")
    return []


@router.get("/start_education/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["api"])
def start_education(name):
    start_educate(f"{projects_dir}/{name}")
    return [c.FireEvent(event=GoToEvent(url=f"/web/project/{name}"))]