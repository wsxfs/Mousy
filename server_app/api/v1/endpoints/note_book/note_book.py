from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from server_app.services.notebook_config import NoteBookModel, NoteRecord
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/get_settings")
async def get_settings(request: Request):
    """获取笔记本设置"""
    return request.app.state.notebook_config.settings

@router.post("/update_all")
async def update_all_settings(request: Request, new_settings: NoteBookModel):
    """批量更新设置"""
    try:
        request.app.state.notebook_config.update_settings(new_settings)
        return {"message": "Settings updated successfully"}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Failed to update settings: {str(e)}"}
        )

@router.post("/blacklist/add")
async def add_to_blacklist(request: Request, record: NoteRecord):
    """添加记录到黑名单"""
    try:
        request.app.state.notebook_config.add_to_blacklist(record)
        return {"message": "Record added to blacklist"}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Failed to add record: {str(e)}"}
        )

@router.post("/whitelist/add")
async def add_to_whitelist(request: Request, record: NoteRecord):
    """添加记录到白名单"""
    try:
        request.app.state.notebook_config.add_to_whitelist(record)
        return {"message": "Record added to whitelist"}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Failed to add record: {str(e)}"}
        )
