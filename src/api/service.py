from flask import Blueprint, request
from flask_cors import CORS, cross_origin
from api.constants.message import *
from handler import DatabaseHandler
from utils import build_response

service_endpoint = Blueprint('service', __name__)
CORS(service_endpoint)

dbh = DatabaseHandler()


@service_endpoint.route('/')
def index():
    return 'service ok!'


@service_endpoint.route("/update_market", methods=["POST"])
@cross_origin()
def update_market():
    if request.method == "POST":
        try:
            data = request.json
        except Exception:
            return build_response(status_code=400, body=FAILED_MISSING_BODY)

        try:
            pair_symbol = data["pair_symbol"]
            if not pair_symbol:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_PAIR)

        try:
            price = data["price"]
            if not price:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_PRICE)

        try:
            orders = dbh.redis_get_orders_at(pair_symbol, float(price))
            map(lambda o: dbh.execute(o), orders)
        except Exception as err:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"Execute orders failed: {err}"
            }
            return build_response(status_code=400, body=body)

        try:
            triggers = dbh.redis_get_triggers_at(pair_symbol, float(price))
            map(lambda t: dbh.trigger(t), triggers)
        except Exception as err:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"Check triggers failed: {err}"
            }
            return build_response(status_code=400, body=body)

        body = {"STATUS": "SUCCESS", "MESSAGE": "Report Price Successfully"}
        return build_response(status_code=200, body=body)
