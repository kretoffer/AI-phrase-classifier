from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import yaml

from config import projects_dir


router = APIRouter()

@router.get("/add_to_dataset/{name}", response_class=HTMLResponse)
def add_to_dataset_web(name: str):
    
    with open("www/templates/add_to_dataset.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    return HTMLResponse(content)

@router.get("/project-info/{name}")
def project_info(name: str):
    return yaml.load(open(f"{projects_dir}/{name}/config.yaml", "r"), Loader=yaml.SafeLoader)