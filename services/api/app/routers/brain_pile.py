import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Header
import db.database as db


router = APIRouter()

@router.post("/new", include_in_schema=False)
async def new_brain_pile(project_id: str, authorization: Annotated[str, Header()]):
    brain_pile = db.new_brain_pile(title = "unnamed brain pile", project_id = project_id)
    return {"pile_id": str(brain_pile.id) }

@router.post("/delete", include_in_schema=False)
async def delete_brain_pile(pile_id: str, authorization: Annotated[str, Header()]):
    print("delete_brain_pile")
    return {"status": "ok"}

@router.post("/archive", include_in_schema=False)
async def archive_brain_drop(pile_id: str, authorization: Annotated[str, Header()]):
    print("archive_brain_pile")
    return {"status": "ok"}

@router.post("/tweak", include_in_schema=False)
async def tweak_brain_drop(direction:str, authorization: Annotated[str, Header()]):
    print("tweak_brain_drop")
    return {"task_id": "task1234"}

@router.post("/promote", include_in_schema=False)
async def promote_tweak(tweak_id:str, authorization: Annotated[str, Header()]):
    print("promote_tweak")
    return {"drop_id": "drop1234"}

@router.post("/add_drop", include_in_schema=False)
async def add_brain_drop(
    title: str, pile_id: str,
    authorization: Annotated[str, Header()]
):
    print("add_brain_drop")
    drop = db.add_brain_drop(title = title, content_url = "", pile_id = pile_id)
    #await agpyutils.storage.copy(auth_header=authorization, request=copy_request)
    #db.set_brain_drop_content(engine=engine, drop_id = drop.id, content_url = copy_request.destination.key)
    return {"drop_id": "drop1234"}

@router.post("/remove_drop", include_in_schema=False)
async def remove_brain_drop(drop_id: str, pile_id: str, authorization: Annotated[str, Header()]):
    print("remove_brain_drop")
    return {"status": "ok"}
