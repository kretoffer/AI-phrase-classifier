from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from src.ui.return_static_html import get_static_html

router = APIRouter()

@router.get("/{project}/edit-hand-element/{id}", response_class=HTMLResponse, tags=["web"])
def edit_hand_element(project: str, id: int):
    return HTMLResponse(get_static_html("edit_dataset_hand"))

@router.get("/{project}/edit-template-element/{id}", response_class=HTMLResponse, tags=["web"])
def edit_template_element(project: str, id: int):
    return HTMLResponse(get_static_html("edit_dataset_template"))
