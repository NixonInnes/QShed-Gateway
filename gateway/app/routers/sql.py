import json
from typing import Union, Dict, List
from fastapi import APIRouter, HTTPException, Request

from qshed.client.models import response as responseModels

from .. import sql_session
from ..sql import Entity


router = APIRouter()

@router.get("/entity/get/{id}", response_model=responseModels.JSONResponse)
def get_sql_entity(id:int):
    entity = sql_session.query(Entity).get(id)
    if entity is None:
        return responseModels.JSONResponse(ok=False, content="", message="id not found")
    return responseModels.JSONResponse(content=entity.json())


@router.get("/entity/all", response_model=responseModels.JSONResponse)
def get_all_sql_entities():
    content = json.dumps([entity.dict() for entity in sql_session.query(Entity).all()])
    return responseModels.JSONResponse(content=content)


@router.get("/entity/roots", response_model=responseModels.JSONResponse)
def get_sql_entity_roots():
    content = json.dumps([entity.dict() for entity in Entity.get_roots()])
    return responseModels.JSONResponse(content=content)


@router.post("/entity/create", response_model=responseModels.JSONResponse)
def create_sql_entity(data: dict):
    try:
        entity = Entity(
            name=data["name"], 
            data=str(data["data"]),  # Converted to string
            type=int(data["type"])
        )
    except:
        return responseModels.JSONResponse(ok=False, content="", message="name and/or data not defined")
    if "parent" in data:
        try:
            entity.parent = sql_session.query(Entity).get(data["parent"])
        except:
            return responseModels.JSONResponse(
                ok=False, 
                message=f"unable to find parent entity with id: {data['parent']}"
            )

    if "children" in data:
        for child in data["children"]:
            try:
                entity.children.append(
                    sql_session.query(Entity).get(child)
                )
            except:
                return responseModels.JSONResponse(
                    ok=False,
                    content="",
                    message=f"unable to find child entity with id: {child}"
                )
    sql_session.add(entity)
    sql_session.commit()
    return responseModels.JSONResponse(
        content=entity.json(), 
        message=f"created new Entity with id: {entity.id}"
    )

