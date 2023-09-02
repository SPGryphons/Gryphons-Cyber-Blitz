"""
The routes for the `/api/` endpoint.
"""

from uuid import uuid4

from flask import Blueprint, redirect, request

from auth import createJWT, decodeJWT, is_authenticated
from database import database
from limiter import limiter
from webhook_logger import wh_logger

api = Blueprint("api", __name__)  # This endpoint is for the api endpoints


@api.route("/login", methods=["POST"])
def api_login():
    data = request.json
    username = data["username"]
    password = data["password"]
    user_id = database.login(username, password)
    if not user_id:
        return {"error": "Invalid username or password."}, 401
    else:
        admin = database.is_admin(user_id)
        token = createJWT(username, admin)
        return {"token": token}, 200


@api.route("/register", methods=["POST"])
@limiter.limit("5 per hour;50 per day")
def api_register():
    data = request.json
    username = data["username"]
    password = data["password"]
    if database.add_user(username, password):
        return "", 200
    else:
        return {"error": "User already exists."}, 400


@api.route("/create", methods=["POST"])
@is_authenticated
def api_create():
    data = decodeJWT(request.cookies.get("token"))

    admin = data["admin"]
    if admin:
        print(f"Attempted post creation by admin. At IP address {request.remote_addr}")
        wh_logger.warning(f"Attempted post creation by admin. At IP address {request.remote_addr}")
        return "No.", 403

    username = data["user"]
    user_id = database.get_user_id(username)
    if not user_id:
        return {"error": "User does not exist."}, 404
    
    posts = database.get_post_by_user(user_id)

    if len(posts) >= 10:
        return {"error": "You have reached the maximum number of posts. Delete a post to make a new one."}, 403

    data = request.json
    title = data["title"]
    content = data["content"]

    if len(content) > 1000:
        return {"error": "Post content is too long."}, 400

    link = str(uuid4())
    # This should never fail cause uuid4
    database.add_post(title, content, link, user_id)
    return {"link": link}, 200


@api.route("/delete/<path:link>", methods=["GET"])
@is_authenticated
def api_delete(link):
    data = decodeJWT(request.cookies.get("token"))
    username = data["user"]
    user_id = database.get_user_id(username)
    if not user_id:
        return {"error": "User does not exist."}, 404

    post = database.get_post_by_link(link)
    if not post:
        return {"error": "Post does not exist."}, 404
    elif post[3] != user_id and not data["admin"]:
        return {"error": "You do not have permission to delete this post."}, 403
    
    database.delete_post(link)
    return redirect("/profile")


@api.route("/view/<path:link>", methods=["GET"])
def api_view(link):
    if request.cookies.get("token") is None:
        username = None
    else:
        data = decodeJWT(request.cookies.get("token"))
        username = data["user"]
        user_id = database.get_user_id(username)
        if not user_id:
            return {"error": "User does not exist."}, 404

    post = database.get_post_by_link(link)
    if not post:
        return {"error": "Post does not exist."}, 404

    # Check if post is approved
    if not post[4]:
        if username is None or (post[3] != user_id and not data["admin"]):
            return {"error": "Post is not approved."}, 403
        elif data["admin"]:
            database.mark_post_as_seen(link)

    return {"title": post[0], "content": post[1]}, 200