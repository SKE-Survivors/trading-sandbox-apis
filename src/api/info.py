from flask import Blueprint, request
from flask_cors import CORS, cross_origin
from mongoengine import errors
from handler import DatabaseHandler, SessionHandler
from utils import build_response

info_endpoint = Blueprint('info', __name__)
CORS(info_endpoint)

dbh = DatabaseHandler()
sh = SessionHandler()


@info_endpoint.route('/')
def index():
    return 'info ok!'


@info_endpoint.route("/pairs", methods=["GET"])
@cross_origin()
def pairs():
    # todo: something (?)
    data = ["btc-usdt", "eth-usdt", "bnb-usdt"]
    body = {"STATUS": "SUCCESS", "MESSAGE": data}
    return build_response(status_code=200, body=body)


@info_endpoint.route("/orders", methods=["GET"])
@cross_origin()
def orders():
    data = dbh.orders()
    body = {"STATUS": "SUCCESS", "MESSAGE": data}
    return build_response(status_code=200, body=body)
