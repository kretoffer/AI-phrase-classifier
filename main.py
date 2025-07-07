from fastapi import FastAPI, Body, Header, Query
from fastapi.responses import RedirectResponse, HTMLResponse

from fastui import FastUI, prebuilt_html, AnyComponent
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import GoToEvent, BackEvent

from pydantic import BaseModel, Field

from typing import Iterable, Literal, List
import os
import yaml
from secrets import token_urlsafe
import json

from config import projects_dir, projects_dir_without_system_dir, more_then_one_user

from src.start_education import start_educate
from src.classifier import classificate


c.Page.model_rebuild()
app = FastAPI()

if projects_dir_without_system_dir:
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
    projects_dir = f"{parent_dir}/{projects_dir}"

if not os.path.exists(projects_dir):
    os.makedirs(projects_dir)

userID = "admin"
if not os.path.exists(f"{projects_dir}/{userID}"):
    os.makedirs(f"{projects_dir}/{userID}")
    with open(f"{projects_dir}/{userID}/user.yaml", "w") as f:
        user_data = {
            "name": userID,
            "password": "admin",
            "projects": []
        }
        yaml.dump(user_data, f, allow_unicode=True, sort_keys=False)

def validate_request_post(userID, data: dict, elements_in_data: Iterable):
    if not userID:
        return {"error": "user identifier not specified"}
    if not all([el in data for el in elements_in_data]):
        return {"error": "not all data specified"}
    if not os.path.exists(projects_dir + "/" + str(userID)):
        return {"error": "user not registered"}


def validate_request_get(userID):
    if not userID:
        return {"error": "user identifier not specified"}
    if not os.path.exists(projects_dir + "/" + str(userID)):
        return {"error": "user not registered"}


@app.post("/new_project")
def new_project(data: dict = Body(), userID: str = Header("admin", alias="userID")):
    if resp := validate_request_post(userID, data, ("name",)):
        return resp

    if os.path.exists(projects_dir+"/"+str(userID)+"/"+str(data["name"])):
        return {"error": "a project with this name already exists"}
    
    os.makedirs(projects_dir+"/"+str(userID)+"/"+str(data["name"]))
    os.makedirs(f"{projects_dir}/{userID}/{data['name']}/models")

    with open(f"{projects_dir}/{userID}/user.yaml", "r+", encoding="utf-8") as f:
        user_data = yaml.safe_load(f)
        user_data["projects"].append(str(data["name"]))
        f.seek(0)
        f.truncate()
        yaml.dump(user_data, f, allow_unicode=True, sort_keys=False)
    
    with open(f"{projects_dir}/{userID}/{data["name"]}/config.yaml", "w", encoding="utf-8") as f:
        project_config = {
            "name": data["name"],
            "status": "work",
            "hidden_layer": 50,
            "epochs": 5,
            "learning_rate": 0.01,
            "embedding_dim": 32,
            "intents": [],
            "entities": [],
            "token": token_urlsafe(32),
            "activation_method": "sigmoid"
        }
        yaml.dump(project_config, f, allow_unicode=True, sort_keys=False)

    with open(f"{projects_dir}/{userID}/{data["name"]}/dataset.json", "x", encoding="utf-8") as f:
        f.write('{"hand-data": [], "template-data": []}')

    
    return {"success": "good"}


@app.post("/update_dataset")
def update_dataset(data: dict = Body(), userID: str = Header("admin", alias="userID")):
    if resp := validate_request_post(userID, data, ("project", "hand-data", "template-data")):
        return resp
    
    if not os.path.exists(projects_dir+"/"+str(userID)+"/"+str(data["project"])):
        return {"error": "no such project exists"}
    
    with open(f"{projects_dir}/{userID}/{data['project']}/dataset.json", "r+", encoding="utf-8") as f:
        dataset = json.load(f)
        dataset["hand-data"].extend(data["hand-data"])
        dataset["template-data"].extend(data["template-data"])
        f.seek(0)
        f.truncate()
        json.dump(dataset, f, ensure_ascii=False, indent=1)

    return {"success": "good"}


@app.get("/start_education")
def start_education(userID: str = Header("admin", alias="userID"), project: str = Header("test", alias="project")):
    start_educate(f"{projects_dir}/{userID}/{project}")
    return {"success": "good"}


@app.post("/create_intent")
def create_intent(data: dict = Body(), userID: str = Header("admin", alias="userID")):
    if resp := validate_request_post(userID, data, ("project", "intents",)):
        return resp
    
    if not os.path.exists(projects_dir+"/"+userID+"/"+str(data["project"])):
        return {"error": "no such project exists"}
    
    with open(f"{projects_dir}/{userID}/{data["project"]}/config.yaml", "r+", encoding="utf-8") as f:
        project_data = yaml.safe_load(f)
        project_data["intents"].extend(data["intents"])
        f.seek(0)
        f.truncate()
        project_data["intents"] = list(set(project_data["intents"]))
        yaml.dump(project_data, f, allow_unicode=True, sort_keys=False)

    return {"success": "good"}
    

@app.post("/create_entity")
def create_entity(data: dict = Body(), userID: str = Header("admin", alias="userID")):
    if resp := validate_request_post(userID, data, ("project", "entities",)):
        return resp
    
    if not os.path.exists(projects_dir+"/"+str(userID)+"/"+str(data["project"])):
        return {"error": "no such project exists"}
    
    with open(f"{projects_dir}/{userID}/{data["project"]}/config.yaml", "r+", encoding="utf-8") as f:
        project_data = yaml.safe_load(f)
        project_data["entities"].extend(data["entities"])
        f.seek(0)
        f.truncate()
        project_data["entities"] = list(set(project_data["entities"]))
        yaml.dump(project_data, f, allow_unicode=True, sort_keys=False)

    return {"success": "good"}


@app.get("/about_me")
def about_me(userID: str = Header("admin", alias="userID")):
    if resp := validate_request_get(userID):
        return resp

    with open(f"{projects_dir}/{userID}/user.yaml") as f:
        user_data = yaml.load(f, Loader=yaml.SafeLoader)
    
    return user_data


@app.get("/reg_user")
def new_user(userID: str = Query("admin", alias="userID"), password: str = Query("admin", alias="password")):
    if not more_then_one_user:
        only_folders = [f for f in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, f))]
        if len(only_folders) >= 1:
            return {"error": "user already created, to create more than one user set it up in the system"}
        
    if os.path.exists(f"{projects_dir}/{userID}"):
        return {"error": "user with this name alredy created"}
    
    os.makedirs(f"{projects_dir}/{userID}")
    with open(f"{projects_dir}/{userID}/user.yaml", "w") as f:
        user_data = {
            "name": userID,
            "password": password,
            "projects": []
        }
        yaml.dump(user_data, f, allow_unicode=True, sort_keys=False)

    return {"success": "good"}


@app.get("/message/{userID}/{project}")
def classificate_hand(userID, project, question:str = Query("Что такое AI-classifier", alias="q")):
    if resp := validate_request_get(userID):
        return resp
    
    if not os.path.exists(projects_dir+"/"+str(userID)+"/"+str(project)):
        return {"error": "no such project exists"}

    intent = classificate(f"{projects_dir}/{userID}/{project}", question)
    return {"intent": intent}

#WEB INTERFACE

@app.get("/")
def main_rout():
    return RedirectResponse(url="/web/")

class Project(BaseModel):
    name: str
    status: Literal["work", "educated", "off", "error"]
    hidden_layer: int = Field(50, gt=0)
    epochs: int = Field(0, gt=-1)
    learning_rate: float = Field(0.01, gt=0)
    embedding_dim: int = Field(32, gt=0)
    intents: List[str]
    activation_method: Literal["sigmoid"]
    entities: List[str]
    token: str

@app.get("/api/web/", response_model=FastUI, response_model_exclude_none=True)
def main_web():
    projects = [f for f in os.listdir(f"{projects_dir}/admin") if os.path.isdir(os.path.join(f"{projects_dir}/admin", f))]
    projects = [Project.model_validate(yaml.load(open(f"{projects_dir}/admin/{el}/config.yaml", "r"), Loader=yaml.SafeLoader)) for el in projects]

    return [
        c.Page(
            components=[ # type: ignore
                c.Heading(text="Projects", level=1),    # type: ignore
                c.Table(
                    data=projects,
                    columns=[
                        DisplayLookup(field="name", on_click=GoToEvent(url="/project/{name}")),
                        DisplayLookup(field="status")
                    ]
                )
            ]
        )
    ]

@app.get("/api/project/{name}", response_model=FastUI, response_model_exclude_none=True)
def project_page(name: str):
    if not os.path.exists(f"{projects_dir}/admin/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Heading(text="Project not exists", level=2)
            ]
        )

    project = Project.model_validate(yaml.load(open(f"{projects_dir}/admin/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))

    return [
        c.Page(
            components=[ # type: ignore
                c.Heading(text=project.name, level=1),
                c.Link(components=[c.Text(text='Back')], on_click=BackEvent()),
                c.Details(data=project),
            ]
        ),
    ]

#END OF FILE

@app.get('/web/{path:path}')
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='classifier web'))
