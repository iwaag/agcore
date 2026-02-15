from typing import Annotated
from fastapi import APIRouter, Depends, Header
from fastapi.responses import PlainTextResponse
import db.database as db
import models.models as models
from agpyutils.auth import get_auth_info, AuthInfo
import agpyutils.storage as storge
from agpyutils.storage import StaticObjectRef
from core.common import CLIEND_ID
from core.keycloak_auth import issue_own_client_access_token

DEFAULT_PROJECT_BG_KEY: str = "default_bg"


router = APIRouter()

@router.post("/new", summary="Create a new project")
async def new_poject(auth: AuthInfo = Depends(get_auth_info)):
    new_project = db.new_project(auth.user_id, title = "unnamed project")
    return {"project_id": new_project.id }

@router.get("/list", summary="List all projects")
async def list_pojects(
    auth: AuthInfo = Depends(get_auth_info)
):
    project_list = db.list_projects()
    return {
        "projects": [
            {"id": project.id, "title": project.title}
            for project in project_list
        ]
    }

@router.post("/set_title", summary="Set project title")
async def new_brain_pile(
    project_id: str,
    title: str,
    auth: AuthInfo = Depends(get_auth_info)
):
    db.set_project_title(project_id = project_id, title = title)
    return {"status": "ok"}

@router.post("/default_bg/set", summary="Get upload URL for default background")
async def set_default_bg(
    project_id: str,
    authorization: Annotated[str, Header()],
    auth_info: AuthInfo = Depends(get_auth_info)
):
    token = await issue_own_client_access_token(auth_info.token)
    url = await storge.get_static_object_upload_url(
        "bearer " + token,
        StaticObjectRef(domain = CLIEND_ID, project_id = project_id, user_id=None, relative_key=DEFAULT_PROJECT_BG_KEY)
    )
    return PlainTextResponse(url)
@router.get("/default_bg/get", summary="Get download URL for default background")
async def set_default_bg(
    project_id: str,
    authorization: Annotated[str, Header()],
    auth_info: AuthInfo = Depends(get_auth_info)
):
    token = await issue_own_client_access_token(auth_info.token)
    url = await storge.get_static_object_download_url(
        "bearer " + token,
        StaticObjectRef(domain = CLIEND_ID, project_id = project_id, user_id=None, relative_key=DEFAULT_PROJECT_BG_KEY)
    )
    return PlainTextResponse(url)