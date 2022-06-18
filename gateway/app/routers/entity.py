from typing import List
from fastapi import APIRouter, HTTPException, Request, Query

from qshed.client.models.data import Entity
from qshed.client.models.response import EntityResponse, EntityListResponse

from gateway.app import sql_session
from gateway.app.models import Entity as sqlEntity


router = APIRouter()


@router.get("/get", response_model=EntityListResponse)
async def get(id: List[int] = Query(default=[])):
    entities = []
    for i in id:
        entity = sql_session.query(sqlEntity).get(i)
        if entity is None:
            raise HTTPException(status_code=404, detail=f"Invalid entity id: {i}")
        entities.append(entity)
    return EntityListResponse(
        data=[entity.build_model() for entity in entities]
    )


@router.get("/get_roots", response_model=EntityListResponse)
async def get_roots():
    entities = sqlEntity.get_roots()
    return EntityListResponse(
        data=[entity.build_model() for entity in entities]
    )


@router.post("/create", response_model=EntityResponse)
async def create(entity: Entity):
    if entity.parent:
        parent = sql_session.query(sqlEntity).get(entity.parent)
        if parent is None:
            raise HTTPException(status_code=400, detail=f"Invalid parent id: {entity.parent}")
    else:
        parent = None

    children = []
    if entity.children:
        for child_id in entity.children:
            child = sql_session.query(sqlEntity).get(child_id)
            if child is None:
                raise HTTPException(status_code=400, detail=f"Invalid child id: {child_id}")
            children.append(child)


    new_entity = sqlEntity.create(
        name=entity.name,
        type=entity.type,
        data=entity.data_,
        parent=parent,
        children=children
    )
    return EntityResponse(
        data=new_entity.build_model()
    )


@router.post("/create_many", response_model=EntityListResponse)
async def create_many(entities: List[Entity]):
    new_entities = []
    for entity in entities:
        if entity.parent:
            parent = sql_session.query(sqlEntity).get(entity.parent)
            if parent is None:
                raise HTTPException(status_code=400, detail=f"Invalid parent id: {entity.parent}")
        else:
            parent = None

        children = []
        if entity.children:
            for child_id in entity.children:
                child = sql_session.query(sqlEntity).get(child_id)
                if child is None:
                    raise HTTPException(status_code=400, detail=f"Invalid child id: {child_id}")
                children.append(child)

        new_entity = sqlEntity.create(
            name=entity.name,
            type=entity.type,
            data=entity.data_,
            parent=parent,
            children=children
        )

        new_entities.append(new_entity)

    return EntityListResponse(
        data=[new_entity.build_model() for new_entity in new_entities]
    )
