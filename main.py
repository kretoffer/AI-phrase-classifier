from fastapi import FastAPI, Body, Header, Query

from typing import Iterable
import os
import yaml
from secrets import token_urlsafe
import json

from config import projects_dir

from src.start_education import start_educate
from src.classifier import classificate


app = FastAPI()

if not os.path.exists(projects_dir):
    os.makedirs(projects_dir)


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
            "status": "work",
            "hidden_layer": 50,
            "epohs": 5,
            "learning_rate": 0.01,
            "embedding_dim": 32,
            "intents": [],
            "entities": [],
            "token": token_urlsafe(32)
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

@app.get("/message/{userID}/{project}")
def classificate_hand(userID, project, question:str = Query("Что такое AI-classifier", alias="q")):
    if resp := validate_request_get(userID):
        return resp
    
    if not os.path.exists(projects_dir+"/"+str(userID)+"/"+str(project)):
        return {"error": "no such project exists"}

    intent = classificate(f"{projects_dir}/{userID}/{project}", question)
    return {"intent": intent}
