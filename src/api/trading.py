from flask import Blueprint, request
from flask_cors import CORS, cross_origin
from api.constants.message import *
from handler import DatabaseHandler, SessionHandler
from utils import build_response

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
        except Exception:
            return build_response(status_code=400, body=FAILED_MISSING_BODY)
        
        try:
            order_id = data["order_id"]
            if not order_id:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_ORDER_ID)


        order = dbh.find_order(order_id)
        if not order:
            return build_response(status_code=400, body=FAILED_ORDER_NOT_EXIST)

        try:
            dbh.cancel_order(order, user)
        except Exception as err:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"Cancel order not allow: {err}"
            }
            return build_response(status_code=400, body=body)

        body = {"STATUS": "SUCCESS", "MESSAGE": "Cancel order Successfully"}
        return build_response(status_code=200, body=body)

    if request.method == "POST":
        try:
            data = request.json
        except Exception:
            return build_response(status_code=400, body=FAILED_MISSING_BODY)

        try:
            status = data["status"]
            if not status:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_STATUS)
        
        try:
            order_flag = data["flag"]
            if not order_flag:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_FLAG)
        
        try:
            pair_symbol = data["pair_symbol"]
            if not pair_symbol:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_PAIR)
        
        try:
            input_amount = data["input_amount"]
            if not input_amount:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_INPUT_AMOUNT)
        
        try:
            output_amount = data["output_amount"]
            if not output_amount:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_OUTPUT_AMOUNT)

        try:
            dbh.create_order(user, status, order_flag, pair_symbol, input_amount, output_amount)
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
        except Exception: 
            return build_response(status_code=400, body=FAILED_MISSING_BODY)
        
        try:
            trigger_id = data["trigger_id"]
            if not trigger_id:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_TRIGGER_ID)

        trigger = dbh.find_trigger(trigger_id)
        if not trigger:
            return build_response(status_code=400, body=FAILED_TRIGGER_NOT_EXIST)

        try:
            dbh.cancel_trigger(trigger, user)
        except Exception as err:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"Cancel trigger not allow: {err}"
            }
            return build_response(status_code=400, body=body)

        body = {"STATUS": "SUCCESS", "MESSAGE": "Cancel trigger Successfully"}
        return build_response(status_code=200, body=body)

    if request.method == "POST":
        try:
            data = request.json
        except Exception:
            return build_response(status_code=400, body=FAILED_MISSING_BODY)
        
        try:
            order_flag = data["flag"]
            if not order_flag:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_FLAG)
        
        try:
            pair_symbol = data["pair_symbol"]
            if not pair_symbol:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_PAIR)
        
        try:
            input_amount = data["input_amount"]
            if not input_amount:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_INPUT_AMOUNT)
        
        try:
            output_amount = data["output_amount"]
            if not output_amount:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_OUTPUT_AMOUNT)
        
        try:
            stop_price = data["stop_price"]
            if not stop_price:
                raise
        except Exception:
            return build_response(status_code=400, body=FAILED_REQUIRE_STOP_LIMIT)
        
        try:
            dbh.create_trigger(user, order_flag, pair_symbol, input_amount, output_amount, stop_price)
        except Exception as err:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"Create trigger failed: {err}"
            }
            return build_response(status_code=400, body=body)

        body = {"STATUS": "SUCCESS", "MESSAGE": "Create trigger successfully"}
        return build_response(status_code=201, body=body)
