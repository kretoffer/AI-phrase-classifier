import os
import shutil
from typing import Annotated, Optional

import yaml
from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from fastui import FastUI
from fastui import components as c
from fastui.events import GoToEvent, PageEvent
from fastui.forms import fastui_form

from config import projects_dir
from src.shemes import Project

router = APIRouter()

@router.post(
    "/delete-project/{name}",
    response_model=FastUI,
    response_model_exclude_none=True,
    tags=["api"],
)
def delete_project(name: str, name_form: str = Form(None, alias="project-name")):
    if not os.path.exists(f"{projects_dir}/{name}"):
        return {"error": "no such project exists"}

    if name != name_form:
        return {"error", "name of project and name in input don't match"}

    shutil.rmtree(f"{projects_dir}/{name}", ignore_errors=True)

    return [c.FireEvent(event=GoToEvent(url="/web/"))]


@router.post(
    "/add-intent-entity/{name}",
    response_model=FastUI,
    response_model_exclude_none=True,
    tags=["api"],
)
def add_intent_or_entity(
    name: str,
    intent_name: Optional[str] = Form(None, alias="intent-name"),
    entity_name: Optional[str] = Form(None, alias="entity-name"),
):
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
        c.FireEvent(event=PageEvent(name="add-entity-modal", clear=True)),
    ]


@router.get("/{project_name}/delete-intent/{intent}", tags=["api"])
def delete_intent(project_name: str, intent: str):
    if not os.path.exists(f"{projects_dir}/{project_name}"):
        return {"error": "no such project exists"}
    with open(
        f"{projects_dir}/{project_name}/config.yaml", "r+", encoding="utf-8"
    ) as f:
        project = Project.model_validate(yaml.load(f, Loader=yaml.SafeLoader))
        if intent not in project.intents:
            return {"error": "no such intent in this project"}
        project.intents.remove(intent)

        f.seek(0)
        f.truncate()
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)

    return RedirectResponse(url=f"/web/project/{project_name}/edit/intents")


@router.get("/{project_name}/delete-entity/{entity}", tags=["api"])
def delete_entity(project_name: str, entity: str):
    if not os.path.exists(f"{projects_dir}/{project_name}"):
        return {"error": "no such project exists"}
    with open(
        f"{projects_dir}/{project_name}/config.yaml", "r+", encoding="utf-8"
    ) as f:
        project = Project.model_validate(yaml.load(f, Loader=yaml.SafeLoader))
        if entity not in project.entities:
            return {"error": "no such entity in this project"}
        project.entities.remove(entity)

        f.seek(0)
        f.truncate()
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)

    return RedirectResponse(url=f"/web/project/{project_name}/edit/entities")
