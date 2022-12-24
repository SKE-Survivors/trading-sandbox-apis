from flask import Blueprint, request
from flask_cors import CORS, cross_origin
from mongoengine import errors
from api.constants.message import *
from handler import DatabaseHandler, SessionHandler
from utils import build_response, encode_pwd, check_pwd

auth_endpoint = Blueprint('auth', __name__)
CORS(auth_endpoint)

dbh = DatabaseHandler()
sh = SessionHandler()


@auth_endpoint.route('/')
def index():
    return 'auth ok!'


@auth_endpoint.route("/signup", methods=["POST"])
@cross_origin()
def signup():
    try:
        data = request.json
        username = data["username"]
        email = data["email"]
        password = data["password"]
        confirm_password = data["confirm-password"]
    except Exception as err:
        return build_response(status_code=400, err=err)

    if not email:
        return build_response(status_code=400, body=FAILED_REQUIRED_EMAIL)
    if not password:
        return build_response(status_code=400, body=FAILED_REQUIRED_PASSWORD)
    if confirm_password != password:
        return build_response(status_code=400, body=FAILED_WRONG_CONFIRM_PASSWORD)

    if dbh.find_user(email):
        body = FAILED_USER_EXIST
        return build_response(status_code=400, body=body)

    try:
        dbh.add_user(
            email=email,
            username=username,
            password=encode_pwd(password),
        )
    except errors.ValidationError as err:  # check email
        body = {"STATUS": "FAILED", "MESSAGE": f"Registration failed: {err}"}
        return build_response(status_code=400, body=body)

    body = {"STATUS": "SUCCESS", "MESSAGE": "Registration Successfully"}
    return build_response(status_code=201, body=body)


@auth_endpoint.route("/login", methods=["POST"])
@cross_origin()
def login():
    try:
        data = request.json
        email = data["email"]
        password = data["password"]
    except Exception as err:
        return build_response(status_code=400, err=err)

    if not email:
        return build_response(status_code=400, body=FAILED_REQUIRED_EMAIL)
    if not password:
        return build_response(status_code=400, body=FAILED_REQUIRED_PASSWORD)

    # check email and password
    user = dbh.find_user(email)
    if not user:
        return build_response(status_code=400, body=FAILED_USER_NOT_EXIST)

    if check_pwd(password, user.password):
        return build_response(status_code=400, body=FAILED_WRONG_PASSWORD)

    # gen token and add to redis
    token = sh.set_session(user.email)
    body = {
        "STATUS": "SUCCESS",
        "MESSAGE": {
            "email": user.email,
            "token": token
        }
    }
    return build_response(status_code=201, body=body)


@auth_endpoint.route("/logout")
@cross_origin()
def logout():
    email = request.args.get("email")

    if not dbh.find_user(email):
        return build_response(status_code=400, body=FAILED_USER_NOT_EXIST)

    sh.remove_session(email)
    body = {"STATUS": "SUCCESS", "MESSAGE": f"Logout successfully"}
    return build_response(status_code=200, body=body)


# for front-end to call before load page
@auth_endpoint.route("/check")
@cross_origin()
def check():
    email = request.args.get("email")
    token = request.args.get("token")

    if not dbh.find_user(email):
        return build_response(status_code=400, body=FAILED_USER_NOT_EXIST)

    msg = "User is authorized" if sh.in_session(
        email, token) else "User is not authorized"

    body = {"STATUS": "SUCCESS", "MESSAGE": msg}
    return build_response(status_code=200, body=body)


@auth_endpoint.route("/user", methods=['GET', 'PUT', 'DELETE'])
@cross_origin()
def user():
    email = request.args.get("email")
    if not email:
        return build_response(status_code=400, body=FAILED_REQUIRED_EMAIL)

    user = dbh.find_user(email)
    if not user:
        return build_response(status_code=400, body=FAILED_USER_NOT_EXIST)

    if request.method == "GET":
        email = user.email
        data = user.view()
        body = {
            "STATUS": "SUCCESS",
            "data": data,
        }

    if request.method == "PUT":
        token = request.args.get("token")

        if not token:
            return build_response(status_code=400, body=FAILED_MISSING_TOKEN)

        try:
            data = request.json
        except Exception:
            return build_response(status_code=400, body=FAILED_MISSING_BODY)

        if not sh.in_session(email, token):
            return build_response(status_code=400, body=FAILED_PERMISSION_DENIED)

        for field in data:
            # note: you can add more field to update here
            if field == "username":
                user.username = data[field]

            if field == "password":
                try:
                    confirm = data["confirm-password"]
                except Exception:
                    return build_response(status_code=400, body=FAILED_REQUIRED_CONFIRM_PASSWORD)

                if data[field] != confirm:
                    return build_response(status_code=400, body=FAILED_WRONG_CONFIRM_PASSWORD)
                user.password = encode_pwd(data[field])

        user.update(**user.info())
        body = {"STATUS": "SUCCESS", "MESSAGE": f"Update user {user.email}"}

    if request.method == "DELETE":
        token = request.args.get("token")

        if not token:
            return build_response(status_code=400, body=FAILED_MISSING_TOKEN)

        if not sh.in_session(email, token):
            return build_response(status_code=400, body=FAILED_PERMISSION_DENIED)

        user.delete()
        body = {"STATUS": "SUCCESS", "MESSAGE": f"Delete user {user.email}"}

    return build_response(status_code=201, body=body)