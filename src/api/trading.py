from flask import Blueprint, request
from flask_cors import CORS, cross_origin
from mongoengine import errors
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
        body = {'STATUS': 'FAILED', 'MESSAGE': 'Missing argument: token'}
        return build_response(status_code=400, body=body)

    user = dbh.find_user(email)
    if not user:
        body = {"STATUS": "FAILED", "MESSAGE": f"User does not exist"}
        return build_response(status_code=400, body=body)

    if not sh.in_session(email, token):
        body = {"STATUS": "FAILED", "MESSAGE": f"Permission denied"}
        return build_response(status_code=400, body=body)

    if request.method == "DELETE":
        try:
            data = request.json
            order_id = data["order_id"]
        except Exception as err:
            return build_response(status_code=400, err=err)

        if not order_id:
            body = {"STATUS": "FAILED", "MESSAGE": f"order_id is required"}
            return build_response(status_code=400, body=body)

        order = dbh.find_order(order_id)
        if not order:
            body = {"STATUS": "FAILED", "MESSAGE": f"Order does not exist"}
            return build_response(status_code=400, body=body)

        try:
            user.cancel_order(order)
        except Exception as err:
            body = {"STATUS": "FAILED", "MESSAGE": f"Cancel order not allow: {err}"}
            return build_response(status_code=400, body=body)

        body = {"STATUS": "SUCCESS", "MESSAGE": "Cancel order Successfully"}
        return build_response(status_code=201, body=body)

    if request.method == "POST":
        try:
            data = request.json
            status = data["status"]
            order_type = data["type"]
            pair_symbol = data["pair_symbol"]
            input_token = data["input_token"]
            input_amount = data["input_amount"]
            output_token = data["output_token"]
            output_amount = data["output_amount"]
        except Exception as err:
            return build_response(status_code=400, err=err)

        if not status:
            body = {"STATUS": "FAILED", "MESSAGE": f"status is required"}
            return build_response(status_code=400, body=body)
        if not order_type:
            body = {"STATUS": "FAILED", "MESSAGE": f"type is required"}
            return build_response(status_code=400, body=body)
        if not pair_symbol:
            body = {"STATUS": "FAILED", "MESSAGE": f"pair_symbol is required"}
            return build_response(status_code=400, body=body)
        if not input_token:
            body = {"STATUS": "FAILED", "MESSAGE": f"input_token is required"}
            return build_response(status_code=400, body=body)
        if not input_amount:
            body = {"STATUS": "FAILED", "MESSAGE": f"input_amount is required"}
            return build_response(status_code=400, body=body)
        if not output_token:
            body = {"STATUS": "FAILED", "MESSAGE": f"output_token is required"}
            return build_response(status_code=400, body=body)
        if not output_amount:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"output_amount is required"
            }
            return build_response(status_code=400, body=body)

        try:
            if not user.check_balance(input_token, input_amount):
                body = {
                    "STATUS": "FAILED",
                    "MESSAGE": f"user balance not enough to create this order"
                }
                return build_response(status_code=400, body=body)

            order = user.create_order(
                status,
                order_type,
                pair_symbol,
                input_token,
                input_amount,
                output_token,
                output_amount,
            )
        except errors.ValidationError as err:
            body = {
                "STATUS": "FAILED",
                "MESSAGE": f"Create order failed: {err}"
            }
            return build_response(status_code=400, body=body)

        # execute order
        if order.status == "finished":
            try:
                user.execute_order(order)
            except Exception as err:
                # todo: rollback order creation?
                body = {
                    "STATUS": "FAILED",
                    "MESSAGE": f"Order created, but execution failed: {err}"
                }
                return build_response(status_code=400, body=body)

        body = {"STATUS": "SUCCESS", "MESSAGE": "Create order successfully"}
        return build_response(status_code=201, body=body)
