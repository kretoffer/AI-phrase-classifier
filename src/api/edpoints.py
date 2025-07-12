import os
from fastapi import APIRouter, Query
import yaml

from src.logic.classifier import classificate

from config import projects_dir


router = APIRouter()

@router.get("/message/{project}", tags=["api"])
def classificate_hand(project, question:str = Query("Что такое AI-classifier", alias="q")):
    
    if not os.path.exists(f"{projects_dir}/{project}"):
        return {"error": "no such project exists"}
    
    if yaml.load(open(f"{projects_dir}/{project}/config.yaml", "r"), Loader=yaml.SafeLoader)["status"] == "off":
        return {"error": "project was off"}

    intent = classificate(f"{projects_dir}/{project}", question)
    return {"intent": intent}