import httpx
from fastapi import APIRouter

from qshed.client.models.data import Schedule
from qshed.client.models.response import (
    ScheduleResponse,
    SchedulesResponse,
    StrResponse,
)

from config import Config


router = APIRouter()


@router.post("/add", response_model=StrResponse)
async def add_schedule(schedule: Schedule):
    async with httpx.AsyncClient() as client:
        resp = await client.post(Config.SCHEDULER_ADDRESS + "/add", data=schedule.json())
    return StrResponse(content=resp.content)


@router.get("/get/{job_id}", response_model=ScheduleResponse)
async def get_schedule(job_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(Config.SCHEDULE_ADDRESS + f"/get/{job_id}")
    return ScheduleResponse(content=resp.content)


@router.get("/list", response_model=SchedulesResponse)
async def list_schedules():
    async with httpx.AsyncClient() as client:
        resp = await client.get(Config.SCHEDULER_ADDRESS + "/list")
    return SchedulesResponse(**resp.json())
