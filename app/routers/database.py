from typing import Union, Dict, List
from fastapi import APIRouter, HTTPException

from qshed.client.models import Request, Schedule

router = APIRouter()


from pydantic import BaseModel

class MongoQuery(BaseModel):
    key: str
    query: Union[str, Dict[str,str]]


class Response(BaseModel):
    ok: bool = True
    message: str = ""

class DictResponse(Response):
    content: Dict[str,str]

class ListResponse(Response):
    content: List[str]

class StrResponse(Response):
    content: str

class IntResponse(Response):
    content: int

class JSONResponse(StrResponse):
    pass


@router.post("/create", response_model=StrResponse)
def create_database(database_name:str):
    """Create a new database.  

    Returns:  
        ok (bool): flag whether the request was successful  
        message (str): status message  
        content (str): name of the newly created database  
    """
    try:
        mongo_client[database_name]
    except Exception as e:
        return HTTPException(status_code=500, detail="Unable to create database")
    return StrResponse(content=database_name, message="database created")


@router.get("/list", response_model=ListResponse)
def list_databases():
    database_names:List[str] = mongo_client.list_database_names()
    return ListResponse(content=database_names, message="databases created")


@router.get("/{database_name}/list", response_model=ListResponse)
def list_collections(database_name:str):
    try:
        db = mongo_client[database_name]
    except:
        return HTTPException(status_code=404, detail="Database not found")

    collection_names = db.list_collection_names()
    return ListResponse(content=collection_names, message=f"{database_name} collections")


@router.get("/{database_name}/{collection_name}/get", response_model=JSONResponse)
def get_collection(database_name:str, collection_name:str):
    return get_limited_collection(database_name, collection_name, 10)


@router.get("/{database_name}/{collection_name}/get/{limit}", response_model=JSONResponse)
def get_limited_collection(database_name:str, collection_name:str, limit:int):
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")

    data = col.find(request.args).sort("$natural", -1).limit(limit)
    return JSONResponse(content=json.dumps(data), message=f"{database_name}/{collection_name} content (limit={limit})")


@router.post("/{database_name}/{collection_name}/insert", response_model=DictResponse)
def insert_into_collection(database_name:str, collection_name:str, data:dict):
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")
    rtn = col.insert_one(data)
    return StrResponse(content=rtn.inserted_id, message=f"data inserted into {database_name}/{collection_name}")


@router.post("/{database_name}/{collection_name}/insert/many")
def insert_many_into_collection(database_name:str, collection_name:str, data:list):
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")

    rtn = col.insert_many(data)
    return ListResponse(content=rtn.inserted_ids, message=f"data inserted into {database_name}/{collection_name}")


@router.post("/{database_name}/{collection_name}/delete/one", response_model=Response)
def delete_one_from_collection(database_name:str, collection_name:str, query:MongoQuery):
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")

    col.delete_one(query)
    return Response(message=f"1 document deleted from {database_name}/{collection_name}")


@router.post("/{database_name}/{collection_name}/delete/many", response_model=IntResponse)
def delete_many_from_collection(database_name:str, collection_name:str, query:MongoQuery):
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")

    rtn = col.delete_many(query)
    return IntResponse(content=rtn.deleted_count, message=f"{rtn.deleted_count} documents deleted from {database_name}/{collection_name}")


@router.post("/{database_name}/{collection_name}/delete/all", response_model=IntResponse)
def delete_all_from_collection(database_name:str, collection_name:str, confirm:bool=False):
    if not confirm:
        return HTTPException(status_code=400, detail="Confirmation option not set")

    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return HTTPException(status_code=404, detail="Database/collection not found")

    rtn = col.delete_many({})
    return IntResponse(content=rtn.deleted_count, message=f"all documents deleted from {database_name}/{collection_name}")