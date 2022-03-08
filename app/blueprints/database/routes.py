import json
from bson.json_util import dumps as bson_dumps
from flask import render_template, redirect, request, url_for, current_app, jsonify

from ... import mongo_client
from . import data_bp


@data_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@data_bp.route("/create", methods=["POST"])
def create_database():
    data = request.get_json(force=True)
    if "database_name" not in data:
        return "malformed data", 400
    mongo_client[data["database_name"]]
    return jsonify({"response": "ok"})

@data_bp.route("/list", methods=["GET"])
def list_databases():
    database_names = mongo_client.list_database_names()
    return json.dumps(database_names)


@data_bp.route("/<database_name>/list")
def list_collections(database_name):
    try:
        db = mongo_client[database_name]
    except:
        return "Not Found", 404

    collection_names = db.list_collection_names()
    return json.dumps(collection_names)


@data_bp.route("/<database_name>/<collection_name>/get")
def get_collection(database_name, collection_name):
    return get_limited_collection(database_name, collection_name, 10)


@data_bp.route("/<database_name>/<collection_name>/get/<int:limit>")
def get_limited_collection(database_name, collection_name, limit):
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return "Not Found", 404

    data = col.find(request.args).sort("$natural", -1).limit(limit)
    return bson_dumps(data)


@data_bp.route("/<database_name>/<collection_name>/insert", methods=["POST"])
def insert_into_collection(database_name, collection_name):
    data = request.get_json(force=True)
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return "Not Found", 404
    rtn = col.insert_one(data)
    return jsonify({"response": f"{rtn.inserted_id}"})


@data_bp.route("/<database_name>/<collection_name>/insert/many", methods=["POST"])
def insert_many_into_collection(database_name, collection_name):
    data = request.get_json(force=True)
    if not isinstance(data, list):
        return "expected list", 400

    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return "Not Found", 404

    rtn = col.insert_many(data)
    return jsonify({"response":f"{rtn.inserted_ids}"})


@data_bp.route("/<database_name>/<collection_name>/delete/one", methods=["POST"])
def delete_one_from_collection(database_name, collection_name):
    data = request.get_json(force=True)
    if "query" not in data:
        return "malformed data", 400
    
    query = data["query"]
    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return "Not Found", 404

    col.delete_one(query)
    return jsonify({"response":"ok"})


@data_bp.route("/<database_name>/<collection_name>/delete/many", methods=["POST"])
def delete_many_from_collection(database_name, collection_name):
    data = request.get_json(force=True)
    if "query" not in data:
        return "malformed data", 400
    
    query = data["query"]
    if not query: # Check for empty dict - this will delete all
        return "please use the delete/all endpoint to delete all collections", 400

    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return "Not Found", 404

    rtn = col.delete_many(query)
    return jsonify({"response": f"ok, {rtn.deleted_count} deleted"})


@data_bp.route("/<database_name>/<collection_name>/delete/all", methods=["POST"])
def delete_all_from_collection(database_name, collection_name):
    data = request.get_json(force=True)
    if "confirm" not in data:
        return "malformed data", 400
    if not data["confirm"]:
        return "confirm statement not found", 400

    try:
        db = mongo_client[database_name]
        col = db[collection_name]
    except:
        return "Not Found", 404

    rtn = col.delete_many({})
    return jsonify({"response": f"ok, {rtn.deleted_count} deleted"})





