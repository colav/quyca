from flask import Blueprint, redirect
from werkzeug import Response

router = Blueprint("docs", __name__)


@router.route("/robots.txt")
def redirect_to_robots() -> Response:
    return redirect("static/robots.txt")


@router.route("/google54c758d287263571.html")
def redirect_to_google() -> Response:
    return redirect("static/google54c758d287263571.html")
