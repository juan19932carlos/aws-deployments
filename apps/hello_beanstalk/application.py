"""WSGI entry point for Elastic Beanstalk.

The EB Python platform starts gunicorn with WSGIPath `application:application`
by default: a module `application.py` at the bundle root exposing a callable
named `application`. Plain WSGI, so no framework or requirements are needed.
"""

import json


def application(environ, start_response):
    body = json.dumps({"message": "hello Laura Sofia Romero"}).encode()
    start_response(
        "200 OK",
        [("Content-Type", "application/json"), ("Content-Length", str(len(body)))],
    )
    return [body]
