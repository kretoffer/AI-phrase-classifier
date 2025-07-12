from fastapi import APIRouter

from src.api.edit_dataset import router as edit_dataset_router
from src.api.edpoints import router as endpoint_router
from src.api.general import router as general_router
from src.api.project_edit_general import router as project_edit_general_router

router = APIRouter()
router.include_router(edit_dataset_router)
router.include_router(endpoint_router)
router.include_router(general_router)
router.include_router(project_edit_general_router)
