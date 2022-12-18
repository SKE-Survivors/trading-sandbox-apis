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
    data = [
        "bnb-busd", "btc-busd", "aud-busd", "ada-busd", "xrp-busd", "ltc-busd",
        "eth-busd", "sol-busd", "cake-busd", "gmt-busd", "shib-busd",
        "doge-busd", "bnb-usdt", "btc-usdt", "aud-usdt", "ada-usdt",
        "xrp-usdt", "ltc-usdt", "eth-usdt", "sol-usdt", "cake-usdt",
        "gmt-usdt", "shib-usdt", "doge-usdt", "ada-bnb", "xrp-bnb", "ltc-bnb",
        "sol-bnb", "cake-bnb", "gmt-bnb", "bnb-btc", "ada-btc", "xrp-btc",
        "ltc-btc", "eth-btc", "sol-btc", "cake-btc", "gmt-btc", "doge-btc",
        "bnb-dai", "btc-dai", "eth-dai", "busd-rub", "usdt-rub", "bnb-rub",
        "btc-rub", "ada-rub", "xrp-rub", "ltc-rub", "eth-rub", "sol-rub",
        "doge-rub", "bnb-aud", "btc-aud", "ada-aud", "xrp-aud", "eth-aud",
        "sol-aud", "gmt-aud", "shib-aud", "doge-aud", "bnb-eth", "shib-doge"
    ]
    body = {"STATUS": "SUCCESS", "MESSAGE": data}
    return build_response(status_code=200, body=body)


@info_endpoint.route("/orders", methods=["GET"])
@cross_origin()
def orders():
    data = dbh.orders()
    body = {"STATUS": "SUCCESS", "MESSAGE": data}
    return build_response(status_code=200, body=body)
