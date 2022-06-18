from bson.json_util import dumps as json_dumps
from typing import Union, Dict, List
from fastapi import APIRouter, HTTPException, Request

from qshed.client.models import (
    response as responseModels,
    data as dataModels
)
from qshed.client.models.misc import MongoQuery

from gateway.app import mongo_client, sql_session
import gateway.app.models as sqlModels


router = APIRouter()


# @router.get("/database/{collection_db_id}", response_model=responseModels.CollectionDatabaseResponse)
# def get_database(collection_db_id: Union[int, str]):
#     if type(collection_db_id) is int:
#         collection_db = sql_session.query(sqlModels.CollectionDatabase).get(collection_db_id)
#     else:
#         collection_db = (
#             sql_session
#             .query(sqlModels.CollectionDatabase)
#             .filter_by(name=collection_db_id)
#             .first()
#         )
#     if collection_db is None:
#         return HTTPException(status_code=404, detail="Collection database not found")
#     return responseModels.CollectionDatabaseResponse(
#         content=collection_db.build_model()
#     )


# @router.get("/database/all", response_model=responseModels.CollectionDatabaseListResponse)
# def get_all_databases(limit: int = 10):
#     collection_dbs = (
#         sql_session
#         .query(sqlModels.CollectionDatabase)
#         .order_by(sqlModels.CollectionDatabase.created_on)
#         .limit(limit)
#         .all()
#     )
#     return responseModels.CollectionDatabaseListResponse(
#         content=[
#             collection_db.build_model()
#             for collection_db in collection_dbs
#         ]
#     )

# @router.get("/database/create", response_model=responseModels.CollectionDatabaseResponse)
# def create_database(database_name: str):
#     if sql_session.query(sqlModels.CollectionDatabase).filter_by(name=database_name).first():
#         return responseModels.CollectionDatabaseResponse(
#             ok=False,
#             content=None,
#             message=f"'{database_name}' already exists"
#         )
#     collection_db = sqlModels.CollectionDatabase.create(database_name)
#     return responseModels.CollectionDatabaseResponse(
#         content=collection_db.build_model()
#     )


# @router.get("/{collection_id}", response_model=responseModels.CollectionResponse)
# def get(collection_id: Union[int, str], limit: int = 10, query: Optional[str] = None):

#     if type(collection_id) is int:
#         collection = sql_session.query(sqlModels.Collection).get(collection_id)
#     else:
#         collection = sql_session.query(sqlModels.Collection).filter_by(name=collection_id).first()

#     if collection is None:
#         return HTTPException(status_code=404, detail="Collection not found")
    
#     if query:
#         query = json.loads(query)
#     else:
#         query = {}
    
#     try:
#         return responseModels.CollectionResponse(
#             content=collection.build_model(limit=limit, query=query)
#         )
#     except Exception as e:
#         return HTTPException(status_code=400, detail=str(e))


# @router.get("/database/{collection_db_id}/all", response_model=responseModels.CollectionListResponse)
# def get_all_from_database(collection_db_id: int, limit: int = 10, query: Optional[str] = None):
#     collection_db = sql_session.query(sqlModels.CollectionDatabase).get(collection_db_id)
#     if collection_db is None:
#         return HTTPException(status_code=404, detail="Collection database not found")
#     if query:
#         query = json.loads(query)
#     else:
#         query = {}
#     try:
#         return responseModels.CollectionListResponse(
#         content=[
#             collection.build_model(limit=limit, query=query)
#             for collection in collection_db.collections
#         ]
#     )
#     except Exception as e:
#         return HTTPException(status_code=400, detail=str(e))
    

# @router.get(
#     "/{database_name}/{collection_name}/get", response_model=responseModels.JSONResponse
# )
# def get_collection(database_name: str, collection_name: str, request: Request):
#     return get_limited_collection(database_name, collection_name, 10)


# @router.get(
#     "/{database_name}/{collection_name}/get/{limit}",
#     response_model=responseModels.JSONResponse,
# )
# def get_limited_collection(
#     database_name: str, collection_name: str, limit: int, request: Request
# ):
#     query = request.query_params._dict
#     try:
#         db = mongo_client[database_name]
#         col = db[collection_name]
#     except:
#         return HTTPException(status_code=404, detail="Database/collection not found")

#     data = json_dumps(col.find(query).sort("$natural", -1).limit(limit))
#     return responseModels.JSONResponse(
#         content=data,
#         message=f"{database_name}/{collection_name} content (limit={limit})",
#     )


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
