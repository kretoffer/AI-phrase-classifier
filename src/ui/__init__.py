from fastapi import APIRouter

from src.ui.edit_ui import router as edit_ui_router
from src.ui.general import router as general_router

router = APIRouter()
router.include_router(edit_ui_router)
router.include_router(general_router)
