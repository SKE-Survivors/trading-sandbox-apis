import json
from flask import Response


def build_response(status_code, body=None, err=None):
    if err:
        message = {"STATUS": "FAILED", "MESSAGE": type(err).__name__}
        return Response(json.dumps(message),
                        status=status_code,
                        mimetype='application/json')
    else:
        return Response(json.dumps(body),
                        status=status_code,
                        mimetype='application/json')
