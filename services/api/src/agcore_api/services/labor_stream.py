import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import AsyncIterator

from fastapi import Request
from fastapi.responses import StreamingResponse
from hatchet_sdk import Hatchet
from pydantic import BaseModel, HttpUrl

hatchet = Hatchet()

HATCHET_LABOR_WORKFLOW_NAME = "labor"
HATCHET_LABOR_LOOKBACK_DAYS = 30
HATCHET_LABOR_LIST_LIMIT = 100


class LaborInfo(BaseModel):
    task_id: str
    workflow_run_id: str
    status: str
    redirect_url: HttpUrl
    created_at: datetime
    hints: dict[str, str] | None = None
    title: str | None = None
    description: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None


class LaborListEvent(BaseModel):
    items: list[LaborInfo]


LABOR_LIST_EVENT_EXAMPLE = {
    "items": [
        {
            "task_id": "2d4ed2eb-9f69-4f4f-b07a-31d9f8e2d4d5",
            "workflow_run_id": "52a4fc41-a9dd-4492-b8a6-f70d781cc02f",
            "status": "RUNNING",
            "redirect_url": "https://example.com/auth/start",
            "created_at": "2026-03-16T10:15:00Z",
            "started_at": "2026-03-16T10:15:02Z",
            "finished_at": None,
            "error_message": None,
        }
    ]
}

def _to_labor_info(run) -> LaborInfo | None:
    input = run.input.get('input')
    redirect_url = input.get('redirect_url')
    hints : dict[str, str] = input.get('hints')
    title = input.get('meta').get('title')
    description = input.get('meta').get('description')
    try:
        return LaborInfo(
            title=title,
            description=description,
            task_id=run.task_external_id,
            workflow_run_id=run.workflow_run_external_id,
            hints=hints,
            status=run.status.value,
            redirect_url=redirect_url,
            created_at=run.created_at,
            started_at=run.started_at,
            finished_at=run.finished_at,
            error_message=run.error_message,
        )
    except Exception:
        logging.exception("failed to serialize labor task: %s", run.task_external_id)
        return None


async def _list_labors_for_user(user_id: str) -> list[LaborInfo]:
    runs = await asyncio.to_thread(
        hatchet.runs.list_with_pagination,
        since=datetime.now(tz=timezone.utc) - timedelta(days=HATCHET_LABOR_LOOKBACK_DAYS),
        limit=HATCHET_LABOR_LIST_LIMIT,
        additional_metadata={
            "user_id": user_id,
            "type_id": "code_auth",
        },
        statuses=["QUEUED", "RUNNING"]

    )

    items = []
    cunter = 0
    for run in runs:
        print(f"run{run.input.get('input').get('redirect_url')}")
        labor = _to_labor_info(run)
        if labor is not None:
            print(f"run{cunter}{labor.model_dump_json()}")
            cunter += 1
            items.append(labor)

    return items


def _encode_sse(event: str, data: BaseModel | dict) -> bytes:
    payload = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    body = f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=True)}\n\n"
    return body.encode("utf-8")


async def stream_labors(request: Request, user_id: str) -> AsyncIterator[bytes]:
    listener = hatchet.listener.stream_by_additional_metadata(
        "user_id",
        user_id,
    )
    last_payload: str | None = None

    try:
        items = await _list_labors_for_user(user_id)
        payload = LaborListEvent(items=items)
        last_payload = payload.model_dump_json()
        yield _encode_sse("labors", payload)

        event_iterator = listener.__aiter__()

        while not await request.is_disconnected():
            try:
                await asyncio.wait_for(event_iterator.__anext__(), timeout=15)
            except TimeoutError:
                yield b": keep-alive\n\n"
                continue
            except StopAsyncIteration:
                break

            items = await _list_labors_for_user(user_id)
            payload = LaborListEvent(items=items)
            current_payload = payload.model_dump_json()

            if current_payload == last_payload:
                continue

            last_payload = current_payload
            yield _encode_sse("labors", payload)
    finally:
        listener.abort()


def create_labor_streaming_response(request: Request, user_id: str) -> StreamingResponse:
    return StreamingResponse(
        stream_labors(request, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
