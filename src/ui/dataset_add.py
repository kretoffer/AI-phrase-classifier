from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from src.ui.return_static_html import get_static_html

router = APIRouter()


@router.get("/add_to_dataset/{name}", response_class=HTMLResponse, tags=["web"])
def add_to_dataset_web(name: str):
    return HTMLResponse(get_static_html("add_to_dataset"))


@router.get(
    "/add_template_to_dataset/{name}", response_class=HTMLResponse, tags=["web"]
)
def add_template_to_dataset_web(name: str):
    return HTMLResponse(get_static_html("add_dataset_template"))
