"""
The routes for the `/` endpoint.
"""

import os

from flask import Blueprint, redirect, render_template, request, send_file

from auth import decodeJWT, is_admin, is_authenticated
from database import database
from webhook_logger import wh_logger

web = Blueprint("web", __name__)  # This endpoint is for the web pages

FLAG = os.getenv("FLAG")

if FLAG is None:
    raise Exception("FLAG is not set in the environment variables, please check your configuration.")


@web.route("/")
def index():
    token = request.cookies.get("token")
    logged_in = False
    admin = False
    if token:
        logged_in = decodeJWT(token)
        admin = logged_in["admin"] if logged_in else False
    return render_template("index.html", logged_in=logged_in, admin=admin)


@web.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_file("./static/img/logo.png")  # This is the logo


@web.route("/login", methods=["GET"])
def login():
    token = request.cookies.get("token")
    if token:
        data = decodeJWT(token)
        if data:
            return redirect("/profile")
    return send_file("./templates/login.html")


@web.route("/register", methods=["GET"])
def register():
    token = request.cookies.get("token")
    if token:
        data = decodeJWT(token)
        if data:
            return redirect("/profile")
    return send_file("./templates/register.html")


@web.route("/logout", methods=["GET"])
def logout():
    response = redirect("/login")
    response.set_cookie("token", "", expires=0)
    return response


@web.route("/flag", methods=["GET"])
@is_admin
def flag():
    try:
        print("Someone got the flag!")
        wh_logger.info(f"Someone got the flag!")
        return render_template("flag.html", flag=FLAG)
    except Exception as e:
        print("Something went wrong")
        wh_logger.error(f"Something went wrong when giving the flag: {e}")
        return "An internal error occurred, please contact Gryphons Support for assistance."


@web.route("/profile", methods=["GET"])
@is_authenticated
def profile():
    data = decodeJWT(request.cookies.get("token"))
    username = data["user"]
    admin = data["admin"]
    user_id = database.get_user_id(username)
    if not user_id:  # This should never happen
        return {"error": "User does not exist."}, 400

    # Render the profile page
    # You can specify more variables to pass to the template
    posts = database.get_post_by_user(user_id)
    return render_template("profile.html", username=username, posts=posts, admin=admin)


@web.route("/create", methods=["GET"])
@is_authenticated
def create():
    data = decodeJWT(request.cookies.get("token"))

    admin = data["admin"]
    if admin:
        return "No.", 403

    username = data["user"]
    user_id = database.get_user_id(username)

    if not user_id:  # This should never happen
        return {"error": "User does not exist."}, 404

    # Render the post page
    return render_template("create.html", username=username)


@web.route("/view/<path:link>", methods=["GET"])
def view(link):
    if request.cookies.get("token") is None:
        username = None
    else:
        data = decodeJWT(request.cookies.get("token"))
        if not data:
            # Delete the cookie then try again
            response = redirect(f"/view/{link}")
            response.set_cookie("token", "", expires=0)
            return response
        username = data["user"]
        user_id = database.get_user_id(username)
        if not user_id:
            return {"error": "User does not exist."}, 404
        
    # Render the view page
    return render_template("view.html", username=username)


@web.route("/403", methods=["GET"])
def error():
    return send_file("./templates/403.html")


@web.route("/<path:path>", methods=["GET"])
def not_found(path):
    print(f"Attempted access to {path} but not found.")
    wh_logger.warning(f"Attempted access to {path} but not found.")
    return send_file("./templates/404.html")