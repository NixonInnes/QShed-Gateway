import httpx
from fastapi import APIRouter

from qshed.client.models import Schedule

router = APIRouter()

SCHEDULER_URL = "http://localhost:5100"


@router.put("/add")
async def add_schedule(schedule: Schedule):
    resp = await httpx.post(SCHEDULER_URL + "/add", data=schedule.json())
    return resp.content

@router.get("/list")
async def list_schedules():
    resp = await httpx.get(SCHEDULER_URL + "/list")
    return resp.content