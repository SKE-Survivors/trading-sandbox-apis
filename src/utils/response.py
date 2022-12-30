import json
from flask import Response


def build_response(status_code: int, body: dict) -> Response:
    return Response(json.dumps(body), status=status_code, mimetype='application/json')
