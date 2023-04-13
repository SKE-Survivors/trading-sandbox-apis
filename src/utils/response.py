import json
from flask import Response


def build_response(status_code: int, body: dict) -> Response:
    return Response(json.dumps(body), status=status_code, mimetype='application/json')

def build_url(url, params: dict):
    p = ""
    for key in params:
        p += key + "=" + params[key] + "&"
    return url + "?" + p[:-1]