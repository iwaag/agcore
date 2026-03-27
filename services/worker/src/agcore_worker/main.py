import os

from hatchet_sdk import ClientConfig, Hatchet
from agpy.task import models
from agcore_worker.tasks.utils import task_unmanaged_labor, task_labor_auth

HATCHET_CLIENT_TOKEN = os.getenv("HATCHET_CLIENT_TOKEN")
HATCHET_CLIENT_HOST_PORT = os.getenv("HATCHET_CLIENT_HOST_PORT")

hatchet = Hatchet(
    # config=ClientConfig(
    #     force_shutdown_on_shutdown_signal=True,
    # ),
)
if __name__ == '__main__':
    worker = hatchet.worker("agcore-worker", workflows=[task_unmanaged_labor, task_labor_auth])
    worker.start()