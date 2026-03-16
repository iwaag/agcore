from datetime import timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from agcore_domain.models import models
from agcore_infra.db import database as db
from agcore_api.services.labor_stream import (
    LABOR_LIST_EVENT_EXAMPLE,
    LaborListEvent,
    create_labor_streaming_response,
)
from agpyutils.auth import get_auth_info, AuthInfo
from pydantic import BaseModel, HttpUrl
from agpyutils.task import get_task_hub, models as task_models

router = APIRouter()
task_hub = get_task_hub()

@router.get("/config/get", summary="Get user config")
async def get_config(auth: AuthInfo = Depends(get_auth_info)) -> models.UserConfig:
    return db.get_user_config(auth.user_id)

@router.post("/config/set", summary="Set user config")
async def set_config(config: models.UserConfig, auth: AuthInfo = Depends(get_auth_info)):
    db.set_user_config(auth.user_id, config)
    return {"status": "ok"}

class NewLaborRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    redirect_url: HttpUrl = None

@router.post("/labor/add", summary="Add labor")
async def add_labor(request: NewLaborRequest, auth: AuthInfo = Depends(get_auth_info)):
    task_hub.request_unmanaged_labor(
        task=task_models.Task_UnmanagedLabor(
            meta=task_models.TaskMetadata(task_id="", user_id=auth.user_id, project_id=""),
            redirect_url="http://test.com", wait_for=timedelta(seconds=5)
        )

    )
@router.post(
    "/labor/list",
    summary="Stream labor list updates",
    description=(
        "Streams the current user's `task_unmanaged_labor` list over Server-Sent Events (SSE).\n\n"
        "Consume this endpoint with `EventSource` or `fetch` plus a stream reader for "
        "`text/event-stream`. The server sends the current list immediately after connection, "
        "then sends the full list again whenever a matching task is updated.\n\n"
        "Each SSE message uses `event: labors`. The `data:` field contains JSON shaped like "
        "`LaborListEvent`."
    ),
    responses={
        200: {
            "description": (
                "SSE stream. Each event uses `event: labors` and `data:` contains the latest labor list JSON."
            ),
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "example": (
                            "event: labors\n"
                            f"data: {LABOR_LIST_EVENT_EXAMPLE}\n\n"
                        ),
                    },
                    "examples": {
                        "initial_event": {
                            "summary": "Initial labor list event",
                            "value": (
                                "event: labors\n"
                                "data: "
                                "{\"items\":[{\"task_id\":\"2d4ed2eb-9f69-4f4f-b07a-31d9f8e2d4d5\","
                                "\"workflow_run_id\":\"52a4fc41-a9dd-4492-b8a6-f70d781cc02f\","
                                "\"status\":\"RUNNING\","
                                "\"redirect_url\":\"https://example.com/auth/start\","
                                "\"created_at\":\"2026-03-16T10:15:00Z\","
                                "\"started_at\":\"2026-03-16T10:15:02Z\","
                                "\"finished_at\":null,"
                                "\"error_message\":null}]}\n\n"
                            ),
                        }
                    },
                },
                "application/json": {
                    "schema": LaborListEvent.model_json_schema(),
                    "example": LABOR_LIST_EVENT_EXAMPLE,
                },
            },
        }
    },
)
async def get_labors(
    request: Request,
    auth: AuthInfo = Depends(get_auth_info),
) -> StreamingResponse:
    return create_labor_streaming_response(request, auth.user_id)
