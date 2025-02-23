from fastapi import APIRouter
from . import note_book

router = APIRouter()
router.include_router(note_book.router, tags=["笔记本"]) 