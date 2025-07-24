from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from src.ui.return_static_html import get_static_html

router = APIRouter()

@router.get("/{project}/edit-hand-element/{id}", response_class=HTMLResponse)
def delete_hand_element(project: str, id: int):
    return HTMLResponse(get_static_html("edit_dataset_hand"))
