from flask import render_template, redirect, request, url_for, current_app

from . import main_bp


@main_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")
