"""
Functions for authenticating users using JWTs.
"""

import datetime
import logging
import os
from functools import wraps

import jwt
from flask import redirect, request, send_file

from database import database
from webhook_logger import wh_logger


BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

if BOT_TOKEN is None or ADMIN_TOKEN is None:
    raise Exception("BOT_TOKEN or ADMIN_TOKEN is not set in the environment variables, please check your configuration.")


def createJWT(username: str, admin: bool) -> str:
    """
    Create a JWT for the user.
    """

    data = {
        "user": username,
        "admin": admin
    }

    if not admin:
        # make token expire if not admin
        expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        data["exp"] = expires

    return jwt.encode(
        data,
        database.JWT_KEY,
        algorithm="HS256"
    )


def decodeJWT(token: str) -> dict | bool:
    """
    Decode a JWT.
    """
    try:
        return jwt.decode(token, database.JWT_KEY, algorithms=["HS256"], options={"verify_exp": True})
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
    except Exception as e:
        print(e)
        wh_logger.error(f"Error decoding JWT: {e}")
        return False
    

def is_authenticated(f):
    """
    Decorator to check if the user is authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the JWT from the cookies
        token = request.cookies.get("token")

        # If the token does not exist, redirect to the login page
        if token is None:
            return redirect("/login")

        # If the JWT is valid, return the function
        data = decodeJWT(token)
        if data:
            # Check if user exists
            if database.get_user_id(data["user"]):
                return f(*args, **kwargs)
            
        # If the user does not exist, or the token is invalid,
        # delete the cookie and redirect to the login page
        response = redirect("/login")
        response.set_cookie("token", "", expires=0)
        return response

    return decorated_function


def is_admin(f):
    """
    Decorator to check if the user is an admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the JWT from the cookies
        token = request.cookies.get("token")

        # If the token does not exist, redirect to the login page
        if token is None:
            return redirect("/403")

        # If the JWT is valid, return the function
        data = decodeJWT(token)
        if data:
            # Check if user is an admin
            if data["admin"]:
                return f(*args, **kwargs)
            else:
                return redirect("/403")
            
        # If the token is invalid,
        # delete the cookie and redirect to the login page
        response = redirect("/login")
        response.set_cookie("token", "", expires=0)
        return response
    
    return decorated_function


def has_token(f):
    """
    Decorator to check if the user has a token.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token is not None:
            if token == BOT_TOKEN or token == ADMIN_TOKEN:
                return f(*args, **kwargs)
            
        cookie = request.cookies.get("api_token")
        if cookie is not None:
            if cookie == BOT_TOKEN or cookie == ADMIN_TOKEN:
                return f(*args, **kwargs)
            
        # If the token is invalid,
        # We return 404 to make it harder for people to find this endpoint 
        logging.warning(f"Someone tried to access {request.path} but was denied, endpoint might be compromised.") 
        wh_logger.warning(f"Someone tried to access {request.path} but was denied, endpoint might be compromised.")
        return send_file("./templates/404.html")
    
    return decorated_function