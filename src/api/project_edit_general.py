import os
import shutil
from typing import Optional
from fastapi import APIRouter, Form
from fastui import FastUI
from fastui import components as c
from fastui.events import GoToEvent, PageEvent
from fastui.forms import fastui_form

from typing import Annotated
import yaml

from config import projects_dir

from src.shemes import Project
from src.shemes.ui_forms import EditForm

router = APIRouter()

@router.post("/update-project/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["api"])
def update_project(name: str, form: Annotated[EditForm, fastui_form(EditForm)]): # type: ignore
    if not os.path.exists(f"{projects_dir}/{name}"):
        return {"error": "no such project exists"}
    
    with open(f"{projects_dir}/{name}/config.yaml", "r+", encoding="utf-8") as f:
        project = Project.model_validate(yaml.load(f, Loader=yaml.SafeLoader))
        project = project.model_copy(update=form.model_dump())
        f.seek(0)
        f.truncate()
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)
    
    return [c.FireEvent(event=GoToEvent(url=f"/web/project/{name}"))]

@router.post("/delete-project/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["api"])
def delete_project(name: str, name_form: str = Form(None, alias="project-name")):
    if not os.path.exists(f"{projects_dir}/{name}"):
        return {"error": "no such project exists"}
    
    if name != name_form:
        return {"error", "name of project and name in input don't match"}
    
    shutil.rmtree(f"{projects_dir}/{name}", ignore_errors=True)
    
    return [c.FireEvent(event=GoToEvent(url="/web/"))]


@router.post("/add-intent-entity/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["api"])
def add_intent_or_entity(name: str, intent_name: Optional[str] = Form(None, alias="intent-name"), entity_name: Optional[str] = Form(None, alias="entity-name")):
    if not os.path.exists(f"{projects_dir}/{name}"):
        return {"error": "no such project exists"}
    
    with open(f"{projects_dir}/{name}/config.yaml", "r+", encoding="utf-8") as f:
        project = Project.model_validate(yaml.load(f, Loader=yaml.SafeLoader))

        if intent_name:
            project.intents.append(intent_name)
        if entity_name:
            project.entities.append(entity_name)

        f.seek(0)
        f.truncate()
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)
    
    return [
        c.FireEvent(event=PageEvent(name="add-intent-modal", clear=True)),
        c.FireEvent(event=PageEvent(name="add-entity-modal", clear=True))
    ]