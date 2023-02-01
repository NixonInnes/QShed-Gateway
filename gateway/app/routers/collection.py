import json
from bson.json_util import dumps as json_dumps
from typing import Union, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Request, Query

from qshed.client.models.response import (
    CollectionResponse,
    CollectionListResponse,
    CollectionDatabaseResponse,
    CollectionDatabaseListResponse,
)
from qshed.client.models.data import Collection, CollectionDatabase

from gateway.app import mongo_client, sql_session
from gateway.app.models import (
    Collection as sqlCollection,
    CollectionDatabase as sqlCollectionDatabase,
    Entity as sqlEntity,
)


router = APIRouter()


@router.get("/get", response_model=CollectionListResponse)
async def get(
    id: List[int] = Query(default=[]), limit: int = 10, query: Optional[str] = None
):
    if query is None:
        query = {}
    else:
        try:
            query = json.loads(query)
        except:
            raise HTTPException(
                status_code=400, detail=f"Invalid Collection query: {q}"
            )

    sql_collections = []
    for i in id:
        sql_collection = sql_session.query(sqlCollection).get(i)
        if sql_collection is None:
            raise HTTPException(status_code=404, detail=f"Invalid Collection id: {i}")
        sql_collections.append(sql_collection)
    return CollectionListResponse(
        data=[
            collection.build_model(query=query, limit=limit)
            for collection in sql_collections
        ]
    )


@router.get("/database/get", response_model=CollectionDatabaseListResponse)
async def get_database(id: List[int] = Query(default=[])):
    sql_collection_dbs = []
    for i in id:
        sql_collection_db = sql_session.query(sqlCollectionDatabase).get(i)
        if sql_collection_db is None:
            raise HTTPException(
                status_code=404, detail=f"Invalid Collection Database id: {i}"
            )
        sql_collection_dbs.append(sql_collection_db)
    return CollectionDatabaseListResponse(
        data=[collection_db.build_model() for collection_db in sql_collection_dbs]
    )


@router.post("/create", response_model=CollectionResponse)
async def create(collection: Collection):
    if collection.entity:
        sql_entity = sql_session.query(sqlEntity).get(collection.entity)
        if sql_entity is None:
            raise HTTPException(
                status_code=404, detail=f"Invalid Entity id: {collection.entity}"
            )
    else:
        sql_entity = None

    sql_collection_db = sql_session.query(sqlCollectionDatabase).get(
        collection.database
    )
    if sql_collection_db is None:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid Collection Database id: {collection.database}",
        )

    sql_collection = sqlCollection.create(
        name=collection.name, database=sql_collection_db
    )

    if collection.data:
        sql_collection.query.insert_one(collection.data)

    return CollectionResponse(data=sql_collection.build_model())


# @router.post("/database/create")
# async def test(r: Request):
#     r = await r.json()
#     breakpoint()
#     return Response(content=r, media_type="application/json")


@router.post("/database/create", response_model=CollectionDatabaseResponse)
async def create_database(collection_db: CollectionDatabase):
    if (
        sql_session.query(sqlCollectionDatabase)
        .filter_by(name=collection_db.name)
        .first()
    ) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Collection Database name already exists: {collection_db.name}",
        )
    sql_collection_db = sqlCollectionDatabase.create(name=collection_db.name)
    return CollectionDatabaseResponse(data=sql_collection_db.build_model())


# @router.post(
#     "/{database_name}/{collection_name}/insert",
#     response_model=responseModels.StrResponse,
# )
# def insert_into_collection(database_name: str, collection_name: str, data: dict):
#     try:
#         db = mongo_client[database_name]
#         col = db[collection_name]
#     except:
#         return HTTPException(status_code=404, detail="Database/collection not found")
#     rtn = col.insert_one(data)
#     return responseModels.StrResponse(
#         content=str(rtn.inserted_id),
#         message=f"data inserted into {database_name}/{collection_name}",
#     )


# @router.post(
#     "/{database_name}/{collection_name}/insert/many",
#     response_model=responseModels.StrListResponse,
# )
# def insert_many_into_collection(database_name: str, collection_name: str, data: list):
#     try:
#         db = mongo_client[database_name]
#         col = db[collection_name]
#     except:
#         return HTTPException(status_code=404, detail="Database/collection not found")

#     rtn = col.insert_many(data)
#     content = [str(i) for i in rtn.inserted_ids]
#     return responseModels.ListResponse(
#         content=content, message=f"data inserted into {database_name}/{collection_name}"
#     )


# @router.post(
#     "/{database_name}/{collection_name}/delete/one",
#     response_model=responseModels.BoolResponse,
# )
# def delete_one_from_collection(
#     database_name: str, collection_name: str, query: MongoQuery
# ):
#     try:
#         db = mongo_client[database_name]
#         col = db[collection_name]
#     except:
#         return HTTPException(status_code=404, detail="Database/collection not found")

#     col.delete_one(query.dict())
#     return responseModels.BoolResponse(
#         content=True,
#         message=f"1 document deleted from {database_name}/{collection_name}"
#     )


# @router.post(
#     "/{database_name}/{collection_name}/delete/many",
#     response_model=responseModels.IntResponse,
# )
# def delete_many_from_collection(
#     database_name: str, collection_name: str, query: MongoQuery
# ):
#     try:
#         db = mongo_client[database_name]
#         col = db[collection_name]
#     except:
#         return HTTPException(status_code=404, detail="Database/collection not found")

#     rtn = col.delete_many(query)
#     return responseModels.IntResponse(
#         content=rtn.deleted_count,
#         message=f"{rtn.deleted_count} documents deleted from {database_name}/{collection_name}",
#     )


# @router.post(
#     "/{database_name}/{collection_name}/delete/all",
#     response_model=responseModels.IntResponse,
# )
# def delete_all_from_collection(
#     database_name: str, collection_name: str, confirm: bool = False
# ):
#     if not confirm:
#         return HTTPException(status_code=400, detail="Confirmation option not set")

#     try:
#         db = mongo_client[database_name]
#         col = db[collection_name]
#     except:
#         return HTTPException(status_code=404, detail="Database/collection not found")

#     rtn = col.delete_many({})
#     return responseModels.IntResponse(
#         content=rtn.deleted_count,
#         message=f"all documents deleted from {database_name}/{collection_name}",
#     )
