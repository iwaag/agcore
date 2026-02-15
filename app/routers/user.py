from typing import Annotated
from fastapi import APIRouter, Depends, Header
import db.database as db
import models.models as models
from agpyutils.auth import get_auth_info, AuthInfo

router = APIRouter()

@router.get("/config/get", summary="Get user config")
async def get_config(auth: AuthInfo = Depends(get_auth_info)) -> models.UserConfig:
    return db.get_user_config(auth.user_id)

@router.post("/config/set", summary="Set user config")
async def set_config(config: models.UserConfig, auth: AuthInfo = Depends(get_auth_info)):
    db.set_user_config(auth.user_id, config)
    return {"status": "ok"}