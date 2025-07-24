from fastapi import APIRouter

from src.ui.edit_ui import router as edit_ui_router
from src.ui.general import router as general_router
from src.ui.dataset_element import router as dataset_element_router

from src.ui.dataset_add import router as dataset_add_router

fastui_router = APIRouter()
fastui_router.include_router(edit_ui_router)
fastui_router.include_router(general_router)

web_router = APIRouter()
web_router.include_router(dataset_add_router)
web_router.include_router(dataset_element_router)
