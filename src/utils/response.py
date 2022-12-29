import json
from flask import Response


def build_response(status_code: int, body: dict, err=None) -> Response:
    if err:
        body["ERROR"] = type(err).__name__

    return Response(json.dumps(body), status=status_code, mimetype='application/json')
