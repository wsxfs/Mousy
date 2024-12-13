from . import champ_select_helper
from fastapi import APIRouter

router = APIRouter()
router.include_router(champ_select_helper.router)