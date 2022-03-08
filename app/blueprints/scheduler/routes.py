import requests
from flask import render_template, redirect, request, url_for, current_app


from . import sched_bp

SCHEDULER_URL = "http://localhost:5100"


@sched_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@sched_bp.route("/add", methods=["POST"])
def add():
    resp = requests.post(SCHEDULER_URL + "/sched", data=request.data)
    return resp.content


@sched_bp.route("/list", methods=["GET"])
def list():
    resp = requests.get(SCHEDULER_URL + "/jobs")
    return resp.content
