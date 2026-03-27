from hatchet_sdk import DurableContext, Hatchet
from agpy.task import models

hatchet = Hatchet()

async def general_unmanaged_labor(input: models.Task_UnmanagedLabor, context: DurableContext) -> dict[str, str]:
    try:
        print("before sleep")
        await context.aio_sleep_for(input.wait_for)
        print("after sleep")
        return {"status": "success",}
    except Exception as e:
        print(e)
        return {"status": "failed",}

@hatchet.durable_task(name="labor", input_validator=models.Task_UnmanagedLabor)
async def task_unmanaged_labor(input: models.Task_UnmanagedLabor, context: DurableContext) -> dict[str, str]:
    return await general_unmanaged_labor(input, context)

@hatchet.durable_task(name="labor_auth", input_validator=models.Task_UnmanagedLabor)
async def task_labor_auth(input: models.Task_UnmanagedLabor, context: DurableContext) -> dict[str, str]:
    return await general_unmanaged_labor(input, context)