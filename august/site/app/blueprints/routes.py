"""
The routes for the application.
"""

from auth import createJWT, has_token, is_admin
from blueprints.api import api
from blueprints.web import web
from database import database


# For adminbot backend to use
@api.route("/g3t_c00ki3_f0r_b0tt_asdaasd")
@has_token
def get_cookie_for_bot():
    cookie = createJWT("adminbot", 1)
    return {"cookie": cookie}, 200


@api.route("/g3t_4ll_p0sts_th4t_4r3_uns33n_asdaasd", methods=["GET"])
@has_token
def get_all_unseen_posts():
    # Return JSON of all unseen posts
    unseen = database.get_all_unseen_posts_links()
    return {"unseen": [link[0] for link in unseen]}, 200


# This is just for debugging purposes
@web.route("/get_all_users_asdaasd", methods=["GET"])
@is_admin
def get_all_users():
    return str(database.get_all_users()), 200


@web.route("/get_all_posts_asdaasd", methods=["GET"])
@is_admin
def get_all_posts():
    return str(database.get_all_posts()), 200