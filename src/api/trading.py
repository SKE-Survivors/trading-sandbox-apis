from flask import Blueprint, request
from flask_cors import CORS, cross_origin
from mongoengine import errors
from api.constants.message import *
from handler import DatabaseHandler, SessionHandler
from utils import build_response, map_pair

trading_endpoint = Blueprint('trading', __name__)
CORS(trading_endpoint)

dbh = DatabaseHandler()
sh = SessionHandler()


@trading_endpoint.route('/')
def index():
    return 'trading ok!'


@trading_endpoint.route("/order", methods=["POST", "DELETE"])
@cross_origin()
def order():
    email = request.args.get("email")
    token = request.args.get("token")

    if not token:
        return build_response(status_code=400, body=FAILED_MISSING_TOKEN)

    user = dbh.find_user(email)
    if not user:
        return build_response(status_code=400, body=FAILED_USER_NOT_EXIST)

    if not sh.in_session(email, token):
        return build_response(status_code=400, body=FAILED_PERMISSION_DENIED)

    if request.method == "DELETE":
        try:
            data = request.json
            order_id = data["order_id"]
        except Exception as err:
            return build_response(status_code=400, body=FAILED_MISSING_BODY, err=err)

        if not order_id:
            return build_response(status_code=400, body=FAILED_REQUIRE_ORDER_ID)

        order = dbh.find_order(order_id)
        if not order:
            return build_response(status_code=400, body=FAILED_ORDER_NOT_EXIST)

        try:
            user.cancel_order(order)
        except Exception as err:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"Cancel order not allow: {err}"
            }
            return build_response(status_code=400, body=body, err=err)

        body = {"STATUS": "SUCCESS", "MESSAGE": "Cancel order Successfully"}
        return build_response(status_code=200, body=body)

    if request.method == "POST":
        try:
            data = request.json
            status = data["status"]
            order_flag = data["flag"]
            pair_symbol = data["pair_symbol"]
            input_amount = data["input_amount"]
            output_amount = data["output_amount"]
        except Exception as err:
            return build_response(status_code=400, body=FAILED_MISSING_BODY, err=err)

        if not status:
            return build_response(status_code=400, body=FAILED_REQUIRE_STATUS)
        if not order_flag:
            return build_response(status_code=400, body=FAILED_REQUIRE_FLAG)
        if not pair_symbol:
            return build_response(status_code=400, body=FAILED_REQUIRE_PAIR)
        if not input_amount:
            return build_response(status_code=400, body=FAILED_REQUIRE_INPUT_AMOUNT)
        if not output_amount:
            return build_response(status_code=400, body=FAILED_REQUIRE_OUTPUT_AMOUNT)

        try:
            order = user.create_order(
                status,
                order_flag,
                pair_symbol,
                input_amount,
                output_amount,
            )
        except Exception as err:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"Create order failed: {err}"
            }
            return build_response(status_code=400, body=body)

        body = {"STATUS": "SUCCESS", "MESSAGE": "Create order successfully"}
        return build_response(status_code=201, body=body)


@trading_endpoint.route("/trigger", methods=["POST", "DELETE"])
@cross_origin()
def trigger():
    email = request.args.get("email")
    token = request.args.get("token")

    if not token:
        return build_response(status_code=400, body=FAILED_MISSING_TOKEN)

    user = dbh.find_user(email)
    if not user:
        return build_response(status_code=400, body=FAILED_USER_NOT_EXIST)

    if not sh.in_session(email, token):
        return build_response(status_code=400, body=FAILED_PERMISSION_DENIED)

    if request.method == "DELETE":
        try:
            data = request.json
            trigger_id = data["trigger_id"]
        except Exception as err: 
            return build_response(status_code=400, body=FAILED_MISSING_BODY, err=err)

        if not trigger_id:
            return build_response(status_code=400, body=FAILED_REQUIRE_TRIGGER_ID)

        trigger = dbh.find_trigger(trigger_id)
        if not trigger:
            return build_response(status_code=400, body=FAILED_TRIGGER_NOT_EXIST)

        try:
            user.cancel_trigger(trigger)
        except Exception as err:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"Cancel trigger not allow: {err}"
            }
            return build_response(status_code=400, body=body)

        body = {"STATUS": "SUCCESS", "MESSAGE": "Cancel trigger Successfully"}
        return build_response(status_code=201, body=body)

    if request.method == "POST":
        try:
            data = request.json
            order_flag = data["flag"]
            pair_symbol = data["pair_symbol"]
            input_amount = data["input_amount"]
            output_amount = data["output_amount"]
            stop_price = data["stop_price"]
        except Exception as err:
            return build_response(status_code=400, body=FAILED_MISSING_BODY, err=err)

        if not order_flag:
            return build_response(status_code=400, body=FAILED_REQUIRE_FLAG)
        if not pair_symbol:
            return build_response(status_code=400, body=FAILED_REQUIRE_PAIR)
        if not input_amount:
            return build_response(status_code=400, body=FAILED_REQUIRE_INPUT_AMOUNT)
        if not output_amount:
            return build_response(status_code=400, body=FAILED_REQUIRE_OUTPUT_AMOUNT)
        if not stop_price:
            return build_response(status_code=400, body=FAILED_REQUIRE_STOP_LIMIT)

        try:
            trigger = user.create_trigger(
                order_flag,
                pair_symbol,
                input_amount,
                output_amount,
                stop_price,
            )
        except Exception as err:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"Create trigger failed: {err}"
            }
            return build_response(status_code=400, body=body)

        body = {"STATUS": "SUCCESS", "MESSAGE": "Create trigger successfully"}
        return build_response(status_code=201, body=body)
