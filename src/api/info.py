from flask import Blueprint, request
from flask_cors import CORS, cross_origin
from handler import DatabaseHandler, SessionHandler
from utils import build_response

info_endpoint = Blueprint('info', __name__)
CORS(info_endpoint)

dbh = DatabaseHandler()
sh = SessionHandler()


@info_endpoint.route('/')
def index():
    return 'info ok!'


PAIRS = [
    "btc-usdt", "eth-usdt", "eth-btc", "bnb-usdt", "bnb-btc", "xrp-usdt",
    "xrp-btc", "bnb-eth", "xrp-bnb", "xrp-eth"
]


@info_endpoint.route("/pairs", methods=["GET"])
@cross_origin()
def pairs():
    body = {"STATUS": "SUCCESS", "MESSAGE": PAIRS}
    return build_response(status_code=200, body=body)


@info_endpoint.route("/orders", methods=["GET"])
@cross_origin()
def orders():
    result = dbh.find_all_orders()

    pair = request.args.get("pair_symbol")
    if pair:
        result = list(filter(lambda order: order['pair_symbol'] == pair, result))

    body = {"STATUS": "SUCCESS", "MESSAGE": result}
    return build_response(status_code=200, body=body)


@info_endpoint.route("/pairs-depth", methods=["GET"])
@cross_origin()
def pairs_depth():
    orders = dbh.find_all_orders()

    result = {}
    for pair in PAIRS:
        result[pair] = len(list(filter(lambda order: order['pair_symbol'] == pair, orders)))

    body = {"STATUS": "SUCCESS", "MESSAGE": result}
    return build_response(status_code=200, body=body)