from bson.json_util import dumps as json_dumps
from typing import Union, Dict, List
from fastapi import APIRouter, HTTPException, Request

from qshed.client.models import response as responseModels
from qshed.client.models.misc import MongoQuery

from .. import mongo_client


router = APIRouter()


@router.post("/create", response_model=responseModels.StrResponse)
def create_database(database_name:str):
    try:
        mongo_client[database_name]
    except Exception as e:
        return HTTPException(status_code=500, detail="Unable to create database")
    return responseModels.StrResponse(content=database_name, message="database created")


@router.get("/list", response_model=responseModels.ListResponse)
def list_databases():
    database_names:List[str] = mongo_client.list_database_names()
    return responseModels.ListResponse(content=database_names, message="databases created")


@router.get("/{database_name}/list", response_model=responseModels.ListResponse)
def list_collections(database_name:str):
    try:
        db = mongo_client[database_name]
    except:
        return HTTPException(status_code=404, detail="Database not found")

    collection_names = db.list_collection_names()
    return responseModels.ListResponse(content=collection_names, message=f"{database_name} collections")


@router.get("/{database_name}/{collection_name}/get", response_model=responseModels.JSONResponse)
def get_collection(database_name:str, collection_name:str, request:Request):
    return get_limited_collection(database_name, collection_name, 10)


@router.get("/{database_name}/{collection_name}/get/{limit}", response_model=responseModels.JSONResponse)
def get_limited_collection(database_name:str, collection_name:str, limit:int, request:Request):
    query = request.query_params._dict
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")

    data = json_dumps(col.find(query).sort("$natural", -1).limit(limit))
    return responseModels.JSONResponse(content=data, message=f"{database_name}/{collection_name} content (limit={limit})")


@router.post("/{database_name}/{collection_name}/insert", response_model=responseModels.DictResponse)
def insert_into_collection(database_name:str, collection_name:str, data:dict):
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")
    rtn = col.insert_one(data)
    return responseModels.StrResponse(content=rtn.inserted_id, message=f"data inserted into {database_name}/{collection_name}")


@router.post("/{database_name}/{collection_name}/insert/many", response_model=responseModels.ListResponse)
def insert_many_into_collection(database_name:str, collection_name:str, data:list):
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")

    rtn = col.insert_many(data)
    return responseModels.ListResponse(content=rtn.inserted_ids, message=f"data inserted into {database_name}/{collection_name}")


@router.post("/{database_name}/{collection_name}/delete/one", response_model=responseModels.Response)
def delete_one_from_collection(database_name:str, collection_name:str, query:MongoQuery):
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")

    col.delete_one(query)
    return responseModels.Response(message=f"1 document deleted from {database_name}/{collection_name}")


@router.post("/{database_name}/{collection_name}/delete/many", response_model=responseModels.IntResponse)
def delete_many_from_collection(database_name:str, collection_name:str, query:MongoQuery):
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")

    rtn = col.delete_many(query)
    return responseModels.IntResponse(content=rtn.deleted_count, message=f"{rtn.deleted_count} documents deleted from {database_name}/{collection_name}")


@router.post("/{database_name}/{collection_name}/delete/all", response_model=responseModels.IntResponse)
def delete_all_from_collection(database_name:str, collection_name:str, confirm:bool=False):
    if not confirm:
        return HTTPException(status_code=400, detail="Confirmation option not set")

    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")

    rtn = col.delete_many({})
    return responseModels.IntResponse(content=rtn.deleted_count, message=f"all documents deleted from {database_name}/{collection_name}")